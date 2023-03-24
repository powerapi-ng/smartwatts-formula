# Copyright (c) 2021, INRIA
# Copyright (c) 2021, University of Lille
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import pymongo


MONGO_URI = "mongodb://127.0.0.1:27017/"
MONGO_INPUT_COLLECTION_NAME = 'test_input_smartwatts'
MONGO_OUTPUT_COLLECTION_NAME = 'test_output_smartwatts'
MONGO_DATABASE_NAME = 'MongoDB1'


def gen_base_db_test(uri, content):
    """
    Create the input database with the provided content. The output database is deleted
    :param uri: The mongo connection URI
    :param content: The database content
    """
    mongo = pymongo.MongoClient(uri)
    db = mongo[MONGO_DATABASE_NAME]

    # delete collection if it already exist
    db[MONGO_INPUT_COLLECTION_NAME].drop()
    db.create_collection(MONGO_INPUT_COLLECTION_NAME)
    for item in content:
        db[MONGO_INPUT_COLLECTION_NAME].insert_one(item)

    # delete output collection
    db[MONGO_OUTPUT_COLLECTION_NAME].drop()
    mongo.close()


def clean_base_db_test(uri):
    """
    drop test_input_smartwatts and test_output_smartwatts collections
    """
    mongo = pymongo.MongoClient(uri)
    db = mongo[MONGO_DATABASE_NAME]
    db[MONGO_INPUT_COLLECTION_NAME].drop()
    db[MONGO_OUTPUT_COLLECTION_NAME].drop()
    mongo.close()
