
import os
import pickle
from datetime import datetime
import numpy as np

import smarttypes, random
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)

from smarttypes.graphreduce import GraphReduce
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_group import TwitterGroup
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_credentials import TwitterCredentials

screen_name = 'SmartTypes'
root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
follower_followies_map = root_user.get_graph_info(distance=0, min_followers=60)
gr = GraphReduce(screen_name, follower_followies_map)
gr.reduce_with_linloglayout()
gr.figure_out_reduction_distances()


#model_user = TwitterUser.by_screen_name('SmartTypes', postgres_handle)
#api_handle = model_user.credentials.api_handle
#api_user = api_handle.get_user(screen_name='SmartTypes')

#print os.path.dirname(os.path.abspath(__file__))
