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

import json
import logging
import random
import time

import tornado.gen
import tornado.ioloop

from ..errors import AdvertiseError
from .response import StatusCode

EXPO_BASE = 1.4  # try this first
MAX_DELAY = 10  # sec
MAX_ATTEMPT = 7  # pow(1.4, 8) > 10
DELAY = 60 * 1000  # ms delay time for successful advertise
FIRST_ADVERTISE_TIME = 30  # sec

log = logging.getLogger('tchannel')


def _prepare_next_ad(attempt_counter):
    delay_time = random.uniform(
        0, min(MAX_DELAY, EXPO_BASE ** attempt_counter)
    )
    attempt_counter = min(attempt_counter, MAX_ATTEMPT)
    return attempt_counter, delay_time


@tornado.gen.coroutine
def _advertise(tchannel, service):
    response = None
    try:
        response = yield tchannel.request(service='hyperbahn').send(
            arg1='ad',  # advertise
            arg2='',
            arg3=json.dumps({
                'services': [
                    {
                        'serviceName': service,
                        'cost': 0,
                    }
                ]
            }),
            headers={'as': 'json'},
            retry_limit=0,
        )
    except Exception as e:  # Big scope to keep it alive.
        log.error('Failed to register with Hyperbahn: %s', e)
    else:
        if response.code != StatusCode.ok:
            log.error('Failed to register with Hyperbahn: %s', response)
        else:
            log.info('Successfully register with Hyperbahn')

    raise tornado.gen.Return(response)


@tornado.gen.coroutine
def _advertise_with_backoff(tchannel, service, timeout=None):
    # first advertise rule apply here.
    attempt_counter = 0
    start = time.time()

    while True:
        if timeout and time.time() - start > timeout:
            raise AdvertiseError("Failed to register with Hyperbahn.")

        response = yield _advertise(tchannel, service)

        if response is not None and response.code is StatusCode.ok:
            break

        attempt_counter += 1
        attempt_counter, delay_time = _prepare_next_ad(attempt_counter)

        yield tornado.gen.sleep(delay_time)

    raise tornado.gen.Return(response)


@tornado.gen.coroutine
def advertise(tchannel, service, routers, timeout=None):
    """Advertise the given TChannel to Hyperbahn using the given name.

    This informs Hyperbahn that the given service is hosted at this TChannel
    at a fixed rate.

    It also tells the TChannel about the given Hyperbahn routers.

    :param tchannel:
        TChannel to register with Hyperbahn
    :param service:
        Name of the service behind this TChannel
    :param routers:
        Seed list of addresses of Hyperbahn routers
    :returns:
        A future that resolves to the remote server's response after the first
        advertise finishes.
    """
    timeout = timeout or FIRST_ADVERTISE_TIME

    for router in routers:
        # We use .get here instead of .add because we don't want to fail if a
        # TChannel already knows about some of the routers.
        tchannel.peers.get(router)

    result = yield _advertise_with_backoff(
        tchannel, service, timeout=timeout
    )

    advertise_loop = tornado.ioloop.PeriodicCallback(
        lambda: _advertise_with_backoff(tchannel, service, timeout=None),
        DELAY,
    )
    advertise_loop.start()

    raise tornado.gen.Return(result)

advertize = advertise  # just in case
