#!/usr/bin/env python3
import sys
sys.path.append(r'C:\Users\morit\Documents\Bachelorarbeit\QGIS\WPS\pywps-4.2.4\pywps')

import pywps
from pywps.app import Service, WPSRequest, Process

def pr1():
    """This is the execute method of the process
    """
    pass


application = Service(processes=[Process(pr1)])