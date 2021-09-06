import logging

from Pab import (
    opcode, recordLength,
    EOPATTR, EFILERR, SUCCESS,
    OPEN, CLOSE, READ, WRITE,
)
from TlsSocket import BAD, TlsSocket

logger = logging.getLogger(__name__)


class TlsFile(object):

    @staticmethod
    def filename():
        # open file in "append" mode, such as:
        #   PI.TLS=<hostname/ipv4-addr>:<port>
        return "TLS="

    def __init__(self, tipi_io):
        self.tipi_io = tipi_io
        self.handles = {}
        self.tlssockets = TlsSocket(tipi_io)

    def handle(self, pab, devname):
        op = opcode(pab)
        if op == OPEN:
            self.open(pab, devname)
        elif op == CLOSE:
            self.close(pab, devname)
        elif op == READ:
            self.read(pab, devname)
        elif op == WRITE:
            self.write(pab, devname)
        else:
            self.tipi_io.send([EOPATTR])

    def close(self, pab, devname):
        logger.info("close devname: %s", devname)
        try:
            if devname in self.handles.keys():
                self.closeConnection(devname)
        except Exception as e:
            logger.error(e, exc_info=True)
        self.tipi_io.send([SUCCESS])

    def closeConnection(self, devname):
        msg = bytearray(3)
        msg[0] = 0x22
        msg[1] = self.handles[devname]
        msg[2] = 0x02
        self.tlssockets.processRequest(msg)
        del(self.handles[devname])

    def open(self, pab, devname):
        logger.debug("open devname: %s", devname)
        try:
            (host, port) = self.parseDev(devname)
            self.connectClient(devname, host, port)
        except Exception as e:
            logger.error(e, exc_info=True)
            self.tipi_io.send([EFILERR])
            return

        recLen = recordLength(pab)
        if recLen == 0:
            recLen = 80
        self.tipi_io.send([SUCCESS])
        self.tipi_io.send([recLen])
        return

    def connectClient(self, devname, host, port):
        handleId = self.tlssockets.allocateHandleId()
        address = host + ':' + port
        msg = bytearray(len(address) + 3)
        msg[0] = 0x22
        msg[1] = handleId
        msg[2] = 0x01
        msg[3:] = bytearray(address, 'ascii')
        res = self.tlssockets.processRequest(msg)
        if res == BAD:
            raise Exception("error opening socket")
        self.handles[devname] = handleId

    def read(self, pab, devname):
        logger.info("read devname: %s", devname)

        self.readConnection(pab, devname)
        return

    def readConnection(self, pab, devname):
        handleId = self.handles[devname]
        msg = bytearray(5)
        buf_len = recordLength(pab)
        msg[0] = 0x22
        msg[1] = handleId
        msg[2] = 0x04
        msg[3] = (buf_len & 0xFF00) >> 8
        msg[4] = buf_len & 0xFF
        res = self.tlssockets.processRequest(msg)
        if res == BAD:
            raise Exception('error reading socket')
        self.tipi_io.send([SUCCESS])
        self.tipi_io.send(res)

    def write(self, pab, devname):
        logger.info("write devname: %s", devname)
        if devname.endswith('BIND'):
            raise Exception('not supported')

        handleId = self.handles[devname]
        self.tipi_io.send([SUCCESS])
        data = self.tipi_io.receive()

        msg = bytearray(len(data) + 3)
        msg[0] = 0x22
        msg[1] = handleId
        msg[2] = 0x03
        msg[3:] = data
        res = self.tlssockets.processRequest(msg)
        if res == BAD:
            raise Exception('failed to write to socket')
        self.tipi_io.send([SUCCESS])

    def parseDev(self, devname):
        parts = devname.split("=")[1].split(":")
        host_iface = parts[0]
        port = parts[1]
        logger.info('tls devname: %s, %s', host_iface, port)
        return (host_iface, port)
