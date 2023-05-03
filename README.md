# smartwatts-formula
[![Join the chat at https://gitter.im/Spirals-Team/powerapi](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Spirals-Team/powerapi?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![License: BSD-3-Clause](https://img.shields.io/pypi/l/smartwatts.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/powerapi-ng/smartwatts-formula/build.yml)](https://github.com/powerapi-ng/smartwatts-formula/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/smartwatts)](https://pypi.org/project/smartwatts/)

SmartWatts is a formula for a self-adaptive software-defined power meter based on the [`PowerAPI framework`](https://github.com/powerapi-ng/powerapi).  
This project is the implementation of the power meter depicted in the [`SmartWatts: Self-Calibrating Software-Defined Power Meter for Containers`](https://ieeexplore.ieee.org/document/9139675) paper published in the 20th IEEE/ACM International Symposium on Cluster, Cloud and Internet Computing (CCGRID).

This project provides a software power meter that estimates the power consumption (CPU/DRAM) of the `software containers` (i.e. Docker containers, Kubernetes pods, Libvirt virtual machines...) running on a system.  

This software power meter is based on `Power Models` that distribute the total energy consumption across the running containers depending on their resource usage.
The `Running Average Power Limit (RAPL)` feature is used to measure the total energy consumption of the CPU/DRAM components, and the `Hardware Performance Counters (HwPC)` are used to measure the resource usage of the containers.

To monitor the Hardware Performance Counters (HwPC) of the software containers running on a Linux system, the [hwpc-sensor](https://github.com/powerapi-ng/hwpc-sensor) project is the preferred solution.
There is currently no support for other client/server platforms such as Windows, MacOS or VMware.

## About
SmartWatts is an open-source project developed by the [Spirals project-team](https://team.inria.fr/spirals), a joint research group between the [University of Lille](https://www.univ-lille.fr) and [Inria](https://www.inria.fr).

The documentation is available [on the PowerAPI website](https://powerapi.org).

## Mailing list
You can follow the latest news and asks questions by subscribing to our <a href="mailto:sympa@inria.fr?subject=subscribe powerapi">mailing list</a>.

## Contributing
If you would like to contribute, you can do so through GitHub by forking the repository and sending a pull request.

When submitting code, please check that it follows [the project's rules](CONTRIBUTING.md) and that the **tests pass**.

## Installation
There is two ways to install official releases of SmartWatts:
- Using the Container image **(recommended)** [from Docker Hub](https://hub.docker.com/r/powerapi/smartwatts-formula) or the [Github Container Registry](https://github.com/powerapi-ng/smartwatts-formula/pkgs/container/smartwatts) ;
- Using the Python package [from Pypi](https://pypi.org/project/smartwatts/).
