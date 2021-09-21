SmartWatts is a software-defined power meter based on the PowerAPI toolkit.
SmartWatts is a configurable software that can estimate the power consumption of
software in real-time. Due to PowerAPI it supports the acquisition of raw
metrics from a wide diversity of sensors (_eg._, physical meters, processor
interfaces, hardware counters, OS counters) and the delivery of power
consumptions via different channels (including file system, network, web,
graphical).

# About

SmartWatts is an open-source project developed by the [Spirals research
group](https://team.inria.fr/spirals) (University of Lille 1 and Inria).

The documentation is available [here](http://powerapi.org).

## Contributing

If you would like to contribute code you can do so through GitHub by forking the
repository and sending a pull request.
You should start by reading the [contribution guide](https://github.com/powerapi-ng/smartwatts-formula/blob/master/contributing.md)

When submitting code, please check that it is conform by using `pylint` and
`flake8` with the configurations files at the root of the project.

## Publications

- **[SmartWatts: Self-Calibrating Software-Defined Power Meter for Containers](https://hal.inria.fr/hal-02470128)**: G. Fieni, R. Rouvoy, L. Seinturier. _IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing_ (CCGrid). May 2020, Melbourne, Australia

## Acknowledgments

SmartWatts is written in [Python](https://www.python.org/) (under [PSF
license](https://docs.python.org/3/license.html)) and built on top of
[PowerAPI](https://github.com/powerapi-ng/powerapi)
