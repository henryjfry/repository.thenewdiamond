import requests # type: ignore
from contextlib import closing # type: ignore
from re import fullmatch # type: ignore
from enum import Enum
import hashlib
from typing import Union, Dict, Optional, Tuple, NamedTuple, Any
from pathlib import Path
from logging import getLogger

path = Union[str, Path]

log = getLogger(__name__)

DownloadCheck = Enum('DownloadCheck', 'completed partial checksum_mismatch size_mismatch') # type: ignore

class DownloadError(Exception): pass

ContentRange = NamedTuple('ContentRange', [('start', int),
                                           ('end', int),
                                           ('total', Optional[int])])


def sha256(filename: path) -> str:
    sha = hashlib.sha256()
    chunksize = 524288

    with Path(filename).open('rb') as f:
        data = f.read(chunksize)
        while data:
            sha.update(data)
            data = f.read(chunksize)
    return sha.hexdigest()


def is_download_complete(filename: Path, sha256sum: str, filesize: int) -> Any:
    D = DownloadCheck # type: Any
    try:
        if sha256sum is not None:
            return D.completed if sha256(filename) == sha256sum else D.checksum_mismatch
        elif filesize is not None:
            return D.completed if filename.stat().st_size == filesize else D.size_mismatch
        else:
            return D.partial
    except (NameError, FileNotFoundError):
        return D.partial


def parse_byte_range(content_range: str) -> ContentRange:
    try:
        start, end, total = fullmatch('bytes (\d+)-(\d+)/(\d+|\*)', content_range).groups()
    except AttributeError:
        raise DownloadError('Invalid Content-Range', content_range)
    else:
        total = int(total) if total != '*' else None
        return ContentRange(int(start), int(end), total)


def get_resource_size(headers: Dict[str, str]) -> Optional[int]:
    cl = headers.get('Content-Length')
    cr = headers.get('Content-Range')
    if cr is not None:
        return parse_byte_range(cr).total
    elif cl:
        return int(cl)


def starting_range(resp, filesize: Optional[int]) -> int:
    '''Find starting index from Content-Range, if any. Warn about problematic ranges'''
    if resp.status_code == 206 and 'Content-Range' in resp.headers:
        cr = parse_byte_range(resp.headers['Content-Range'])
        if filesize and filesize != cr.start:
            log.warning('The download is not resuming exactly where it ended')
        if cr.total and cr.end != cr.total - 1:
            log.warning("The download won't fetch the whole file,"
                        " you might want to run urlretrieve again")
        return cr.start
    else:
        return 0


def write_response(resp, filename: Path, reporthook,
                   size: Optional[int], remote_size: Optional[int]):
    if size is None or size != remote_size:
        with filename.open('r+b') if filename.exists() else filename.open('xb') as f:
            start = starting_range(resp, size)
            f.seek(start)
            chunk_size = 16384
            for i, chunk in enumerate(resp.iter_content(chunk_size=chunk_size), start // chunk_size):
                if chunk:
                    f.write(chunk)
                    if reporthook:
                        reporthook(i, chunk_size, remote_size or -1)
            f.flush()


def urlretrieve(url: str, filename: path, reporthook=None, method='GET',
                sha256sum=None, filesize=None, headers=None,
                **kwargs) -> Dict[str, str]:
    D = DownloadCheck # type: Any
    filename = Path(filename)
    if is_download_complete(filename, sha256sum, filesize) != D.completed:
        size = filename.stat().st_size if filename.exists() else None
        headers = headers or {}
        headers.update({'Range': 'bytes=%s-' % size} if size is not None else {})
        with closing(requests.request(method, url, stream=True,
                                      headers=headers, **kwargs)) as resp:
            remote_size = get_resource_size(resp.headers)
            already_completed = resp.status_code == 416
            if not already_completed:
                try:
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    raise DownloadError(e)
                write_response(resp, filename, reporthook, size, remote_size)
                check = is_download_complete(filename, sha256sum, filesize)
                if check not in (D.completed, D.partial):
                    raise DownloadError(check)
            return resp.headers
