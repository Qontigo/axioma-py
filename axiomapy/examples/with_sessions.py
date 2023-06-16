"""
Copyright © 2022 Qontigo GmbH.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

"""
#!/usr/bin/env python
# coding: utf-8

# # Axiomasessions 
# 
# Sample code for how to create and manage sessions for accessing the Axioma api.  
# An Axiomasession provides a global session context that, when authenticated, will be used to run any api queries.  
# The global or current session can be changed and set at any time by accessing the current property of the AxiomaSession class.
# 
# We will use the following methods: 
# 
# **get_session()** -> returns an uninitialised  
# **init()** -> authenticates a session  
# **use_session()** -> will get and init a session that is set as the current session

# ### Imports  
# 
# Use the AxiomaSession



from axiomapy import AxiomaSession


# ### Optional Logging



import logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)-8s %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')


# ### Credentials  
# Load up some credentials to work with. There is a sample.credentials.yaml in the ./examples/credentials folder. Copy this file to credentials.yaml and update the values for the three users to run this example. Alternatively, skip the next set of code and set the credentials directly in the code below:




# Load credentials from file 
from load_credentials import get_user
user1 =  get_user('user1')
user2 = get_user('user2')
user3 = get_user('user3')


# ### Activating a Session
# 
# Create, initialize, and set a session. The active session can be get/set through the current property.



# Get and use a session:
AxiomaSession.use_session(user1['username'], user1['password'], user1['domain'])
me = AxiomaSession.current.test()

# Access the context's current session:
user1_session = AxiomaSession.current
me1 = user1_session.test()

# Activate session using speicifc client id
AxiomaSession.use_session(user1['username'], user1['password'], user1['domain'], user1['client_id'])
me = AxiomaSession.current.test()


# ### Contexts
#   
# Different sessions can be used under different contexts using with blocks.  
# The **get_session()** method gets a new session that can be initialized when entering a new context.  
# If the session was initialized before entering the context it will not be closed when leaving (see session 2 below).
# Using contexts allows you to move data/entities between sessions.



user2_session = AxiomaSession.get_session(user2['username'], user2['password'], user2['domain'])
# Initialize the session if it is to be used outside the context. Otherwise, the session  
# will be open (init) and closed for the context and will require init to be called again.
user2_session.init()
# make a request with this session:
with user2_session:
    print("Running test - should be connection 2")
    me2 = AxiomaSession.current.test()
    with AxiomaSession.get_session(user3['username'], user3['password'], user3['domain']):
        print("Running test - should be connection 3")
        me3 = AxiomaSession.current.test()
    print("Running test - should be connection 2")
    me2_check = AxiomaSession.current.test()
    assert me2.get('userLogin') == me2_check.get('userLogin')


# Check the global context is session1:
print("Running test - should be connection 1")
me1_check = AxiomaSession.current.test()
assert me1.get('userLogin') == me1_check.get('userLogin')


# ### Switching Sessions in the Context Manually  
# 
# The global context session can be specified as needed.  
# 
# 



# Set the session to user 2 (you will also need to init again as it was closed by the with block):
AxiomaSession.current = user2_session
print("Running test - should be connection 2")
me2_check = AxiomaSession.current.test()
assert me2.get('userLogin') == me2_check.get('userLogin')

# Set back to the original session:
AxiomaSession.current = user1_session
print("Running test - should be connection 1")
me1_check = AxiomaSession.current.test()
assert me1.get('userLogin') == me1_check.get('userLogin')




print("Closing open sessions")
user2_session.close()
user1_session.close()
print("Finished")

