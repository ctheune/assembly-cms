#!/bin/bash

bin/test-core && bin/test-workflow && bin/test-translation && bin/test-schedule && bin/test-contact

echo "Success $?"
