#!/usr/bin/env python3

"""
a rough utility to count 
. known containers
. running containers
. kernels per (running) container

it is overlapping monitor but with a troubleshooting-oriented display
"""

import asyncio
import re

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import docker

from nbhosting.stats.monitor import MonitoredJupyter, CourseFigures

loop = asyncio.get_event_loop()

def main():

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("patterns", nargs='*')
    args = parser.parse_args()
    
    def in_scope(container):
        if not args.patterns:
            return True
        else:
            return any(re.match(pattern, container.name)
                       for pattern in args.patterns)

    ban = 10 * '*'
    proxy = docker.from_env()
    containers = proxy.containers.list(all=True)
    running = [ c for c in containers if c.status == 'running' and in_scope(c)]
    idle = [ c for c in containers if c.status != 'running' and in_scope(c)]

    print(ban, "{} idle containers".format(len(idle)))
    print(ban, "{} running containers".format(len(running)))
    for container in running:
        name = container.name
        course, student = name.split('-x-')
        # create one figures instance per container
        figures = CourseFigures()
        monitored = MonitoredJupyter(container, course, student, figures)
        loop.run_until_complete(monitored.count_running_kernels())
        nb_kernels = figures.running_kernels
        print("{:40s} {} kernels".format(container.name, nb_kernels))

if __name__ == '__main__':
    main()
          
