# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from __future__ import absolute_import

from tornado import ioloop

from service import KeyValue
from tchannel.tornado import TChannel


app = TChannel('keyvalue-server', hostport='localhost:8889')


values = {'hello': 'world'}


@app.register(KeyValue)
def getValue(request, response):
    key = request.args.key
    value = values.get(key)

    if value is None:
        raise KeyValue.NotFoundError(key)

    return value


@app.register(KeyValue)
def setValue(request, response):
    key = request.args.key
    value = request.args.value
    values[key] = value


def run():
    app.listen()


if __name__ == '__main__':
    run()
    ioloop.IOLoop.current().start()
