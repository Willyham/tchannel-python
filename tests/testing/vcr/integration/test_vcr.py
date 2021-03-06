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
from tornado import gen

from tchannel.errors import ProtocolError
from tchannel.thrift import client_for
from tchannel.tornado import TChannel
from tchannel.testing import vcr


@pytest.fixture
def call(mock_server):
    channel = TChannel('test-client')

    def f(endpoint, body, headers=None, service=None, scheme=None):
        return channel.request(
            hostport=mock_server.hostport,
            service=service,
            arg_scheme=scheme,
        ).send(endpoint, headers or '', body)

    return f


@pytest.fixture
def thrift_client(thrift_service, mock_server):
    return client_for('myservice', thrift_service)(
        tchannel=TChannel('thrift-client'),
        hostport=mock_server.hostport,
    )


@pytest.mark.gen_test
def test_record_success(tmpdir, mock_server, call):
    path = tmpdir.join('data.yaml')

    mock_server.expect_call('hello').and_write('world').once()

    with vcr.use_cassette(str(path)) as cass:
        response = yield call('hello', 'world', service='hello_service')
        assert 'world' == (yield response.get_body())

    assert cass.play_count == 0
    assert path.check(file=True)

    with vcr.use_cassette(str(path)) as cass:
        response = yield call('hello', 'world', service='hello_service')
        assert 'world' == (yield response.get_body())

    assert cass.play_count == 1


@pytest.mark.gen_test
def test_record_success_thrift(
    tmpdir, mock_server, thrift_service, thrift_client
):
    path = tmpdir.join('data.yaml')
    expected_item = thrift_service.Item(
        'foo', thrift_service.Value(stringValue='bar')
    )
    mock_server.expect_call(thrift_service, method='getItem').and_result(
        expected_item
    ).once()

    with vcr.use_cassette(str(path)) as cass:
        item = yield thrift_client.getItem('foo')
        assert item == expected_item

    assert cass.play_count == 0
    assert path.check(file=True)

    with vcr.use_cassette(str(path)) as cass:
        item = yield thrift_client.getItem('foo')
        assert item == expected_item

    assert cass.play_count == 1


@pytest.mark.gen_test
def test_protocol_exception(tmpdir, mock_server, call):
    path = tmpdir.join('data.yaml')

    mock_server.expect_call('hello').and_raise(
        Exception('great sadness')
    ).once()

    with pytest.raises(ProtocolError):
        with vcr.use_cassette(str(path)):
            yield call('hello', 'world')

    assert not path.check()  # nothing should've been recorded


@pytest.mark.gen_test
def test_record_thrift_exception(
    tmpdir, mock_server, thrift_service, thrift_client
):
    path = tmpdir.join('data.yaml')

    mock_server.expect_call(thrift_service, method='getItem').and_raise(
        thrift_service.ItemDoesNotExist('foo')
    ).once()

    with vcr.use_cassette(str(path)) as cass:
        with pytest.raises(thrift_service.ItemDoesNotExist):
            yield thrift_client.getItem('foo')

    assert cass.play_count == 0
    assert path.check(file=True)

    with vcr.use_cassette(str(path)) as cass:
        with pytest.raises(thrift_service.ItemDoesNotExist):
            yield thrift_client.getItem('foo')

    assert cass.play_count == 1


@pytest.mark.gen_test
def test_use_cassette_as_decorator(tmpdir, mock_server, call):
    path = tmpdir.join('data.yaml')
    mock_server.expect_call('hello').and_write('world').once()

    @gen.coroutine
    @vcr.use_cassette(str(path))
    def f():
        response = yield call('hello', 'world', service='hello_service')
        body = yield response.get_body()
        raise gen.Return(body)

    body = yield f()
    assert body == 'world'

    body = yield f()
    assert body == 'world'


@pytest.mark.gen_test
def test_use_cassette_as_decorator_with_inject(tmpdir, mock_server, call):
    path = tmpdir.join('data.yaml')
    mock_server.expect_call('hello').and_raise(Exception('great sadness'))

    @gen.coroutine
    @vcr.use_cassette(str(path), inject=True)
    def f(cassette):
        with pytest.raises(ProtocolError):
            yield call('hello', 'world', service='hello_service')

        assert len(cassette.data) == 0
        assert cassette.play_count == 0

    yield f()
    yield f()
