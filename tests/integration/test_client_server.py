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

import pytest

from tchannel import tcurl
from tchannel.errors import ConnectionClosedError
from tchannel.errors import TChannelError
from tchannel.tornado import TChannel
from tchannel.tornado.connection import StreamConnection
from tchannel.tornado.stream import InMemStream
from tests.util import big_arg


@pytest.mark.gen_test
def test_tornado_client_with_server_not_there():
    with pytest.raises(ConnectionClosedError):
        yield StreamConnection.outgoing(
            # Try a random port that we're not listening on.
            # This should fail.
            'localhost:41942'
        )


# TODO test case will fail due to StreamClosedError when
# increase the LARGE_AMOUNT to even bigger
@pytest.mark.gen_test
@pytest.mark.parametrize('arg2, arg3', [
    ("", big_arg()),
    (big_arg(), ""),
    ("test", big_arg()),
    (big_arg(),  "test"),
    (big_arg(), big_arg()),
    ("", ""),
    ("test", "test"),
],
    ids=lambda arg: str(len(arg))
)
def test_tchannel_call_request_fragment(mock_server,
                                        arg2, arg3):
    endpoint = b'tchannelpeertest'

    mock_server.expect_call(endpoint).and_write(
        headers=endpoint, body=arg3
    )

    tchannel = TChannel(name='test')
    response = yield tchannel.request(mock_server.hostport).send(
        InMemStream(endpoint), InMemStream(arg2), InMemStream(arg3)
    )
    header = yield response.get_header()
    body = yield response.get_body()
    assert header == endpoint
    assert body == arg3
    assert response.headers['as'] == 'raw'


@pytest.mark.gen_test
def test_tcurl(mock_server):
    endpoint = b'tcurltest'

    mock_server.expect_call(endpoint).and_write(
        headers=endpoint,
        body="hello"
    )

    hostport = 'localhost:%d/%s' % (
        mock_server.port, endpoint.decode('ascii')
    )
    responses = yield tcurl.main(['--host', hostport, '-d', ''])

    # TODO: get multiple requests working here
    assert len(responses) == 1

    for response in responses:
        header = yield response.get_header()
        body = yield response.get_body()
        assert header == endpoint
        assert body == "hello"


@pytest.mark.gen_test
def test_endpoint_not_found(mock_server):
    endpoint = b'tchanneltest'
    mock_server.expect_call(endpoint).and_write(
        headers=endpoint,
        body='world'
    )
    tchannel = TChannel(name='test')

    with pytest.raises(TChannelError):
        yield tchannel.request(
            mock_server.hostport
        ).send(InMemStream(), InMemStream(), InMemStream())
