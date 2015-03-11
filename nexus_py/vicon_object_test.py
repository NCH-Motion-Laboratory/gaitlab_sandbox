# -*- coding: utf-8 -*-
"""

Test the Vicon object for communicating with Vicon Nexus application.
Works with Nexus 2.1.x
@author: jussi
"""
import sys
import ViconNexus

# these needed for Nexus 2.1
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Python")
# needed at least when running outside Nexus
sys.path.append("C:\Program Files (x86)\Vicon\Nexus2.1\SDK\Win32")

# Python objects communicate directly with the Nexus application.
# Before using the vicon object, Nexus needs to be started and a subject loaded.

vicon = ViconNexus.ViconNexus()



