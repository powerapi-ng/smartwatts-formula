# Copyright (c) 2022, INRIA
# Copyright (c) 2022, University of Lille
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
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

# pylint: disable=too-many-lines, redefined-outer-name

import pytest


@pytest.fixture
def smartwatts_timeline_with_mperf_0(smartwatts_timeline):
    """
    Define MPERF = 0 for every report in the given list for all target
    :param smartwatts_timeline: List of reports
    :return The modified report list
    """
    found_second_time = False
    for report in smartwatts_timeline:
        if report['target'] == 'all':
            if found_second_time:
                for n in range(8):
                    smartwatts_timeline[1]['groups']['msr']['0'][str(n)]['MPERF'] = 0
                    smartwatts_timeline[1]['groups']['msr']['0'][str(n)]['APERF'] = 0
                    smartwatts_timeline[1]['groups']['msr']['0'][str(n)]['TSC'] = 0
                return smartwatts_timeline
            found_second_time = True

    return smartwatts_timeline


@pytest.fixture
def smartwatts_timeline_without_hwpc_for_first_tick(smartwatts_timeline):
    """
    Return a list of reports without hwpc
    :param smartwatts_timeline: List of reports
    :return: List of reports without hwpc
    """
    timeline = []
    for report in smartwatts_timeline:
        if report['timestamp'] == '2021-01-13T09:51:22.630':
            if report['target'] == 'all':
                timeline.append(report)
        else:
            timeline.append(report)
    return timeline


@pytest.fixture
def smartwatts_timeline():
    """
    Return a list of reports
    :return: List of reports
    """
    return [
        {
            "timestamp": "2021-01-13T09:51:22.630",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 79254,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2383,
                            "time_enabled": 122154,
                            "time_running": 122154,
                            "LLC_MISSES": 4103,
                            "INSTRUCTIONS_RETIRED": 24072
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 51635,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1553,
                            "time_enabled": 108519,
                            "time_running": 108519,
                            "LLC_MISSES": 642,
                            "INSTRUCTIONS_RETIRED": 18021
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 63518,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1910,
                            "time_enabled": 101443,
                            "time_running": 101443,
                            "LLC_MISSES": 2336,
                            "INSTRUCTIONS_RETIRED": 23063
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 131742,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3961,
                            "time_enabled": 209288,
                            "time_running": 209288,
                            "LLC_MISSES": 5967,
                            "INSTRUCTIONS_RETIRED": 55970
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 75510,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2271,
                            "time_enabled": 167403,
                            "time_running": 167403,
                            "LLC_MISSES": 1077,
                            "INSTRUCTIONS_RETIRED": 31693
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 43801,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1318,
                            "time_enabled": 99324,
                            "time_running": 99324,
                            "LLC_MISSES": 750,
                            "INSTRUCTIONS_RETIRED": 15011
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 75943,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2284,
                            "time_enabled": 118303,
                            "time_running": 118303,
                            "LLC_MISSES": 2028,
                            "INSTRUCTIONS_RETIRED": 18388
                        }
                    }
                }
            }
        },
        {
            "timestamp": "2021-01-13T09:51:22.630",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5709496320,
                            "time_enabled": 1006717449,
                            "time_running": 1006717449
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 10186295,
                            "APERF": 6150323,
                            "TSC": 2121754824,
                            "time_enabled": 1006413700,
                            "time_running": 1006413700
                        },
                        "4": {
                            "MPERF": 24201573,
                            "APERF": 10436356,
                            "TSC": 2121865508,
                            "time_enabled": 1006472122,
                            "time_running": 1006472122
                        },
                        "5": {
                            "MPERF": 17879092,
                            "APERF": 10289712,
                            "TSC": 2121984872,
                            "time_enabled": 1006530973,
                            "time_running": 1006530973
                        },
                        "6": {
                            "MPERF": 34007870,
                            "APERF": 15421716,
                            "TSC": 2122038304,
                            "time_enabled": 1006558126,
                            "time_running": 1006558126
                        },
                        "7": {
                            "MPERF": 13972511,
                            "APERF": 5978347,
                            "TSC": 2122110822,
                            "time_enabled": 1006566148,
                            "time_running": 1006566148
                        },
                        "0": {
                            "MPERF": 29646849,
                            "APERF": 12319312,
                            "TSC": 2122153094,
                            "time_enabled": 1006580601,
                            "time_running": 1006580601
                        },
                        "1": {
                            "MPERF": 20587012,
                            "APERF": 19838920,
                            "TSC": 2122185970,
                            "time_enabled": 1006560540,
                            "time_running": 1006560540
                        },
                        "2": {
                            "MPERF": 14593955,
                            "APERF": 8920739,
                            "TSC": 2122333634,
                            "time_enabled": 1006640193,
                            "time_running": 1006640193
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29a7391b52aff60cb25",
            "timestamp": "2021-01-13T09:51:22.630",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 523558,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15743,
                            "time_enabled": 776267,
                            "time_running": 776267,
                            "LLC_MISSES": 36075,
                            "INSTRUCTIONS_RETIRED": 156161
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 736796,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 22157,
                            "time_enabled": 1188332,
                            "time_running": 1188332,
                            "LLC_MISSES": 47853,
                            "INSTRUCTIONS_RETIRED": 247959
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 350678,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10545,
                            "time_enabled": 649281,
                            "time_running": 649281,
                            "LLC_MISSES": 19895,
                            "INSTRUCTIONS_RETIRED": 89412
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 466103,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 14016,
                            "time_enabled": 634350,
                            "time_running": 634350,
                            "LLC_MISSES": 28115,
                            "INSTRUCTIONS_RETIRED": 175997
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3282451,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 98702,
                            "time_enabled": 4438891,
                            "time_running": 4438891,
                            "LLC_MISSES": 121118,
                            "INSTRUCTIONS_RETIRED": 2872655
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 122499,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3683,
                            "time_enabled": 179754,
                            "time_running": 179754,
                            "LLC_MISSES": 8023,
                            "INSTRUCTIONS_RETIRED": 41321
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29a7391b52aff60cb26",
            "timestamp": "2021-01-13T09:51:22.630",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 932307,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 16283,
                            "time_enabled": 711870,
                            "time_running": 711870,
                            "LLC_MISSES": 11876,
                            "INSTRUCTIONS_RETIRED": 158847
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3845305,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 102779,
                            "time_enabled": 4313669,
                            "time_running": 4313669,
                            "LLC_MISSES": 53091,
                            "INSTRUCTIONS_RETIRED": 5482273
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1084259,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 28975,
                            "time_enabled": 1240389,
                            "time_running": 1240389,
                            "LLC_MISSES": 22033,
                            "INSTRUCTIONS_RETIRED": 408392
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1023975,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 27363,
                            "time_enabled": 1185371,
                            "time_running": 1185371,
                            "LLC_MISSES": 9612,
                            "INSTRUCTIONS_RETIRED": 389700
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 516766,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 13804,
                            "time_enabled": 593259,
                            "time_running": 593259,
                            "LLC_MISSES": 5062,
                            "INSTRUCTIONS_RETIRED": 303980
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3727,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 95,
                            "time_enabled": 22468,
                            "time_running": 22468,
                            "LLC_MISSES": 39,
                            "INSTRUCTIONS_RETIRED": 1144
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29b7391b52aff60cb27",
            "timestamp": "2021-01-13T09:51:23.634",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 79966,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2404,
                            "time_enabled": 243781,
                            "time_running": 243781,
                            "LLC_MISSES": 2644,
                            "INSTRUCTIONS_RETIRED": 17919
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 74202,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2230,
                            "time_enabled": 250607,
                            "time_running": 250607,
                            "LLC_MISSES": 1207,
                            "INSTRUCTIONS_RETIRED": 25014
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 57182,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1720,
                            "time_enabled": 193906,
                            "time_running": 193906,
                            "LLC_MISSES": 2912,
                            "INSTRUCTIONS_RETIRED": 23349
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 36468,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1097,
                            "time_enabled": 273288,
                            "time_running": 273288,
                            "LLC_MISSES": 439,
                            "INSTRUCTIONS_RETIRED": 11901
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 97831,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2941,
                            "time_enabled": 379222,
                            "time_running": 379222,
                            "LLC_MISSES": 1305,
                            "INSTRUCTIONS_RETIRED": 37515
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 98534,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2962,
                            "time_enabled": 271864,
                            "time_running": 271864,
                            "LLC_MISSES": 2477,
                            "INSTRUCTIONS_RETIRED": 29464
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 136169,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4096,
                            "time_enabled": 331245,
                            "time_running": 331245,
                            "LLC_MISSES": 7542,
                            "INSTRUCTIONS_RETIRED": 45303
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29b7391b52aff60cb28",
            "timestamp": "2021-01-13T09:51:23.634",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 4756602880,
                            "time_enabled": 2011233300,
                            "time_running": 2011233300
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 4752431,
                            "APERF": 2542677,
                            "TSC": 2121494506,
                            "time_enabled": 2010928072,
                            "time_running": 2010928072
                        },
                        "4": {
                            "MPERF": 23093108,
                            "APERF": 9333701,
                            "TSC": 2121467464,
                            "time_enabled": 2010973566,
                            "time_running": 2010973566
                        },
                        "5": {
                            "MPERF": 13880066,
                            "APERF": 5376448,
                            "TSC": 2121453548,
                            "time_enabled": 2011017165,
                            "time_running": 2011017165
                        },
                        "6": {
                            "MPERF": 9545363,
                            "APERF": 3877961,
                            "TSC": 2121464084,
                            "time_enabled": 2011048390,
                            "time_running": 2011048390
                        },
                        "7": {
                            "MPERF": 14475942,
                            "APERF": 5799602,
                            "TSC": 2121461394,
                            "time_enabled": 2011053753,
                            "time_running": 2011053753
                        },
                        "0": {
                            "MPERF": 27022770,
                            "APERF": 10524839,
                            "TSC": 2121472778,
                            "time_enabled": 2011070843,
                            "time_running": 2011070843
                        },
                        "1": {
                            "MPERF": 12590496,
                            "APERF": 7092487,
                            "TSC": 2121551428,
                            "time_enabled": 2011091143,
                            "time_running": 2011091143
                        },
                        "2": {
                            "MPERF": 11859317,
                            "APERF": 4612257,
                            "TSC": 2121439040,
                            "time_enabled": 2011139246,
                            "time_running": 2011139246
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29b7391b52aff60cb29",
            "timestamp": "2021-01-13T09:51:23.634",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 477467,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12776,
                            "time_enabled": 1291219,
                            "time_running": 1291219,
                            "LLC_MISSES": 3925,
                            "INSTRUCTIONS_RETIRED": 339647
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3729742,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 99691,
                            "time_enabled": 8497513,
                            "time_running": 8497513,
                            "LLC_MISSES": 54815,
                            "INSTRUCTIONS_RETIRED": 5404864
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 378346,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10210,
                            "time_enabled": 1691977,
                            "time_running": 1691977,
                            "LLC_MISSES": 3396,
                            "INSTRUCTIONS_RETIRED": 300259
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 432540,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 11650,
                            "time_enabled": 1696238,
                            "time_running": 1696238,
                            "LLC_MISSES": 3624,
                            "INSTRUCTIONS_RETIRED": 324906
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 490873,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 13204,
                            "time_enabled": 1172963,
                            "time_running": 1172963,
                            "LLC_MISSES": 4738,
                            "INSTRUCTIONS_RETIRED": 282609
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1550795,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 18060,
                            "time_enabled": 814324,
                            "time_running": 814324,
                            "LLC_MISSES": 18466,
                            "INSTRUCTIONS_RETIRED": 1592132
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29b7391b52aff60cb2a",
            "timestamp": "2021-01-13T09:51:23.634",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 527537,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15864,
                            "time_enabled": 1555604,
                            "time_running": 1555604,
                            "LLC_MISSES": 37270,
                            "INSTRUCTIONS_RETIRED": 155978
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 569846,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 17057,
                            "time_enabled": 2168262,
                            "time_running": 2168262,
                            "LLC_MISSES": 35911,
                            "INSTRUCTIONS_RETIRED": 167011
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 205990,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5249,
                            "time_enabled": 979934,
                            "time_running": 979934,
                            "LLC_MISSES": 11261,
                            "INSTRUCTIONS_RETIRED": 47462
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 42666,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1283,
                            "time_enabled": 712156,
                            "time_running": 712156,
                            "LLC_MISSES": 3055,
                            "INSTRUCTIONS_RETIRED": 8398
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3266655,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 97462,
                            "time_enabled": 8819812,
                            "time_running": 8819812,
                            "LLC_MISSES": 117646,
                            "INSTRUCTIONS_RETIRED": 2890475
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1571702,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15436,
                            "time_enabled": 862656,
                            "time_running": 862656,
                            "LLC_MISSES": 34900,
                            "INSTRUCTIONS_RETIRED": 580236
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29c7391b52aff60cb2b",
            "timestamp": "2021-01-13T09:51:24.639",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 564811,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12475,
                            "time_enabled": 1826547,
                            "time_running": 1826547,
                            "LLC_MISSES": 5273,
                            "INSTRUCTIONS_RETIRED": 380784
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3788221,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 96983,
                            "time_enabled": 12582598,
                            "time_running": 12582598,
                            "LLC_MISSES": 51998,
                            "INSTRUCTIONS_RETIRED": 5429849
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 524998,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 11344,
                            "time_enabled": 2180466,
                            "time_running": 2180466,
                            "LLC_MISSES": 4491,
                            "INSTRUCTIONS_RETIRED": 358683
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 450636,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8729,
                            "time_enabled": 2096069,
                            "time_running": 2096069,
                            "LLC_MISSES": 3875,
                            "INSTRUCTIONS_RETIRED": 327293
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 520482,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 7061,
                            "time_enabled": 1483184,
                            "time_running": 1483184,
                            "LLC_MISSES": 5704,
                            "INSTRUCTIONS_RETIRED": 318746
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1669699,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 44630,
                            "time_enabled": 2750764,
                            "time_running": 2750764,
                            "LLC_MISSES": 19103,
                            "INSTRUCTIONS_RETIRED": 1587742
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29c7391b52aff60cb2c",
            "timestamp": "2021-01-13T09:51:24.639",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 67008,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2015,
                            "time_enabled": 349310,
                            "time_running": 349310,
                            "LLC_MISSES": 3316,
                            "INSTRUCTIONS_RETIRED": 22760
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 27027,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 812,
                            "time_enabled": 308350,
                            "time_running": 308350,
                            "LLC_MISSES": 419,
                            "INSTRUCTIONS_RETIRED": 8881
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 67561,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2032,
                            "time_enabled": 299280,
                            "time_running": 299280,
                            "LLC_MISSES": 3428,
                            "INSTRUCTIONS_RETIRED": 34239
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 76230,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 764,
                            "time_enabled": 313660,
                            "time_running": 313660,
                            "LLC_MISSES": 2814,
                            "INSTRUCTIONS_RETIRED": 25028
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 67850,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1378,
                            "time_enabled": 477625,
                            "time_running": 477625,
                            "LLC_MISSES": 1034,
                            "INSTRUCTIONS_RETIRED": 25084
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 46063,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1004,
                            "time_enabled": 343893,
                            "time_running": 343893,
                            "LLC_MISSES": 501,
                            "INSTRUCTIONS_RETIRED": 15005
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 135497,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2709,
                            "time_enabled": 474720,
                            "time_running": 474720,
                            "LLC_MISSES": 4180,
                            "INSTRUCTIONS_RETIRED": 29628
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29c7391b52aff60cb2d",
            "timestamp": "2021-01-13T09:51:24.639",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5782110208,
                            "time_enabled": 3015246666,
                            "time_running": 3015246666
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 25168625,
                            "APERF": 13899578,
                            "TSC": 2121102742,
                            "time_enabled": 3015252682,
                            "time_running": 3015252682
                        },
                        "4": {
                            "MPERF": 34872043,
                            "APERF": 24129433,
                            "TSC": 2121040782,
                            "time_enabled": 3015265883,
                            "time_running": 3015265883
                        },
                        "5": {
                            "MPERF": 15339167,
                            "APERF": 10295674,
                            "TSC": 2120972322,
                            "time_enabled": 3015278462,
                            "time_running": 3015278462
                        },
                        "6": {
                            "MPERF": 90098743,
                            "APERF": 81972184,
                            "TSC": 2120923488,
                            "time_enabled": 3015283462,
                            "time_running": 3015283462
                        },
                        "7": {
                            "MPERF": 28877033,
                            "APERF": 22922003,
                            "TSC": 2120870468,
                            "time_enabled": 3015262290,
                            "time_running": 3015262290
                        },
                        "0": {
                            "MPERF": 37437316,
                            "APERF": 19835239,
                            "TSC": 2120834694,
                            "time_enabled": 3015259501,
                            "time_running": 3015259501
                        },
                        "1": {
                            "MPERF": 22316138,
                            "APERF": 12948387,
                            "TSC": 2120702022,
                            "time_enabled": 3015220827,
                            "time_running": 3015220827
                        },
                        "2": {
                            "MPERF": 16551248,
                            "APERF": 10110711,
                            "TSC": 2120630782,
                            "time_enabled": 3015234822,
                            "time_running": 3015234822
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29c7391b52aff60cb2e",
            "timestamp": "2021-01-13T09:51:24.639",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 514223,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 14006,
                            "time_enabled": 2246929,
                            "time_running": 2246929,
                            "LLC_MISSES": 37234,
                            "INSTRUCTIONS_RETIRED": 151921
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 518687,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 14111,
                            "time_enabled": 3006816,
                            "time_running": 3006816,
                            "LLC_MISSES": 34369,
                            "INSTRUCTIONS_RETIRED": 144911
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 210419,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5624,
                            "time_enabled": 1335732,
                            "time_running": 1335732,
                            "LLC_MISSES": 13424,
                            "INSTRUCTIONS_RETIRED": 47549
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 40258,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1077,
                            "time_enabled": 779282,
                            "time_running": 779282,
                            "LLC_MISSES": 2757,
                            "INSTRUCTIONS_RETIRED": 8294
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3408969,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 90356,
                            "time_enabled": 12882736,
                            "time_running": 12882736,
                            "LLC_MISSES": 131447,
                            "INSTRUCTIONS_RETIRED": 2915349
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1625531,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 43447,
                            "time_enabled": 2754802,
                            "time_running": 2754802,
                            "LLC_MISSES": 37310,
                            "INSTRUCTIONS_RETIRED": 596455
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29d7391b52aff60cb2f",
            "timestamp": "2021-01-13T09:51:25.643",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 68622,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1834,
                            "time_enabled": 445199,
                            "time_running": 445199,
                            "LLC_MISSES": 1914,
                            "INSTRUCTIONS_RETIRED": 13693
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 67246,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1875,
                            "time_enabled": 427803,
                            "time_running": 427803,
                            "LLC_MISSES": 1124,
                            "INSTRUCTIONS_RETIRED": 25020
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 116176,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3300,
                            "time_enabled": 475267,
                            "time_running": 475267,
                            "LLC_MISSES": 5309,
                            "INSTRUCTIONS_RETIRED": 43875
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 37772,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1135,
                            "time_enabled": 380886,
                            "time_running": 380886,
                            "LLC_MISSES": 403,
                            "INSTRUCTIONS_RETIRED": 11606
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 99280,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2866,
                            "time_enabled": 681046,
                            "time_running": 681046,
                            "LLC_MISSES": 1350,
                            "INSTRUCTIONS_RETIRED": 38014
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 27411,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 732,
                            "time_enabled": 395911,
                            "time_running": 395911,
                            "LLC_MISSES": 493,
                            "INSTRUCTIONS_RETIRED": 8874
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 141679,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4026,
                            "time_enabled": 683789,
                            "time_running": 683789,
                            "LLC_MISSES": 7862,
                            "INSTRUCTIONS_RETIRED": 45543
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29d7391b52aff60cb30",
            "timestamp": "2021-01-13T09:51:25.643",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 738030,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 20010,
                            "time_enabled": 3269087,
                            "time_running": 3269087,
                            "LLC_MISSES": 45456,
                            "INSTRUCTIONS_RETIRED": 223055
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 558951,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15548,
                            "time_enabled": 3948132,
                            "time_running": 3948132,
                            "LLC_MISSES": 30280,
                            "INSTRUCTIONS_RETIRED": 159067
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 5785129,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 154172,
                            "time_enabled": 8154008,
                            "time_running": 8154008,
                            "LLC_MISSES": 184375,
                            "INSTRUCTIONS_RETIRED": 4071902
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 231778,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6359,
                            "time_enabled": 1164414,
                            "time_running": 1164414,
                            "LLC_MISSES": 12543,
                            "INSTRUCTIONS_RETIRED": 55541
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3650088,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 98081,
                            "time_enabled": 17368438,
                            "time_running": 17368438,
                            "LLC_MISSES": 153929,
                            "INSTRUCTIONS_RETIRED": 2979569
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2001390,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 27580,
                            "time_enabled": 4124538,
                            "time_running": 4124538,
                            "LLC_MISSES": 55460,
                            "INSTRUCTIONS_RETIRED": 703260
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29d7391b52aff60cb31",
            "timestamp": "2021-01-13T09:51:25.643",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5478547456,
                            "time_enabled": 4020029654,
                            "time_running": 4020029654
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 10794465,
                            "APERF": 5252366,
                            "TSC": 2121531610,
                            "time_enabled": 4019772228,
                            "time_running": 4019772228
                        },
                        "4": {
                            "MPERF": 30476235,
                            "APERF": 15617329,
                            "TSC": 2121600060,
                            "time_enabled": 4019817257,
                            "time_running": 4019817257
                        },
                        "5": {
                            "MPERF": 16827822,
                            "APERF": 7230869,
                            "TSC": 2121630464,
                            "time_enabled": 4019842282,
                            "time_running": 4019842282
                        },
                        "6": {
                            "MPERF": 43922287,
                            "APERF": 18204745,
                            "TSC": 2121685568,
                            "time_enabled": 4019873242,
                            "time_running": 4019873242
                        },
                        "7": {
                            "MPERF": 9151164,
                            "APERF": 3920923,
                            "TSC": 2121741590,
                            "time_enabled": 4019878169,
                            "time_running": 4019878169
                        },
                        "0": {
                            "MPERF": 26673522,
                            "APERF": 13278626,
                            "TSC": 2121805942,
                            "time_enabled": 4019905306,
                            "time_running": 4019905306
                        },
                        "1": {
                            "MPERF": 13642103,
                            "APERF": 7883229,
                            "TSC": 2121841978,
                            "time_enabled": 4019891800,
                            "time_running": 4019891800
                        },
                        "2": {
                            "MPERF": 17380828,
                            "APERF": 7220756,
                            "TSC": 2121922946,
                            "time_enabled": 4019940206,
                            "time_running": 4019940206
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29d7391b52aff60cb32",
            "timestamp": "2021-01-13T09:51:25.643",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 423314,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6454,
                            "time_enabled": 2117704,
                            "time_running": 2117704,
                            "LLC_MISSES": 4221,
                            "INSTRUCTIONS_RETIRED": 327652
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3722538,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 99500,
                            "time_enabled": 16758562,
                            "time_running": 16758562,
                            "LLC_MISSES": 51330,
                            "INSTRUCTIONS_RETIRED": 5412570
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 415400,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6770,
                            "time_enabled": 2481127,
                            "time_running": 2481127,
                            "LLC_MISSES": 3492,
                            "INSTRUCTIONS_RETIRED": 364268
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 471527,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 9140,
                            "time_enabled": 2500913,
                            "time_running": 2500913,
                            "LLC_MISSES": 3749,
                            "INSTRUCTIONS_RETIRED": 355771
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 565679,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12909,
                            "time_enabled": 2042705,
                            "time_running": 2042705,
                            "LLC_MISSES": 5887,
                            "INSTRUCTIONS_RETIRED": 350214
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1571223,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15749,
                            "time_enabled": 3434319,
                            "time_running": 3434319,
                            "LLC_MISSES": 18170,
                            "INSTRUCTIONS_RETIRED": 1560522
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29e7391b52aff60cb33",
            "timestamp": "2021-01-13T09:51:26.647",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 470989,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10562,
                            "time_enabled": 2573868,
                            "time_running": 2573868,
                            "LLC_MISSES": 4483,
                            "INSTRUCTIONS_RETIRED": 347216
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3775791,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 86550,
                            "time_enabled": 20419200,
                            "time_running": 20419200,
                            "LLC_MISSES": 53552,
                            "INSTRUCTIONS_RETIRED": 5427260
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 419872,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8977,
                            "time_enabled": 2871993,
                            "time_running": 2871993,
                            "LLC_MISSES": 4018,
                            "INSTRUCTIONS_RETIRED": 292973
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 366988,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6644,
                            "time_enabled": 2793966,
                            "time_running": 2793966,
                            "LLC_MISSES": 3247,
                            "INSTRUCTIONS_RETIRED": 306576
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 480004,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6345,
                            "time_enabled": 2324099,
                            "time_running": 2324099,
                            "LLC_MISSES": 5050,
                            "INSTRUCTIONS_RETIRED": 288571
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1655982,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 44263,
                            "time_enabled": 5356828,
                            "time_running": 5356828,
                            "LLC_MISSES": 19171,
                            "INSTRUCTIONS_RETIRED": 1592779
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29e7391b52aff60cb34",
            "timestamp": "2021-01-13T09:51:26.647",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 4963172352,
                            "time_enabled": 5023746191,
                            "time_running": 5023746191
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 10396450,
                            "APERF": 4287609,
                            "TSC": 2120374434,
                            "time_enabled": 5023751525,
                            "time_running": 5023751525
                        },
                        "4": {
                            "MPERF": 15261443,
                            "APERF": 6861925,
                            "TSC": 2120318554,
                            "time_enabled": 5023764697,
                            "time_running": 5023764697
                        },
                        "5": {
                            "MPERF": 13096401,
                            "APERF": 5260397,
                            "TSC": 2120289526,
                            "time_enabled": 5023777320,
                            "time_running": 5023777320
                        },
                        "6": {
                            "MPERF": 4414479,
                            "APERF": 1914461,
                            "TSC": 2120234672,
                            "time_enabled": 5023781890,
                            "time_running": 5023781890
                        },
                        "7": {
                            "MPERF": 8959982,
                            "APERF": 3577339,
                            "TSC": 2120182042,
                            "time_enabled": 5023760933,
                            "time_running": 5023760933
                        },
                        "0": {
                            "MPERF": 19587230,
                            "APERF": 7876888,
                            "TSC": 2120135192,
                            "time_enabled": 5023762645,
                            "time_running": 5023762645
                        },
                        "1": {
                            "MPERF": 22720964,
                            "APERF": 9234630,
                            "TSC": 2120076094,
                            "time_enabled": 5023725156,
                            "time_running": 5023725156
                        },
                        "2": {
                            "MPERF": 12296355,
                            "APERF": 4835113,
                            "TSC": 2119980340,
                            "time_enabled": 5023738867,
                            "time_running": 5023738867
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29e7391b52aff60cb35",
            "timestamp": "2021-01-13T09:51:26.647",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 545892,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15846,
                            "time_enabled": 4022149,
                            "time_running": 4022149,
                            "LLC_MISSES": 36926,
                            "INSTRUCTIONS_RETIRED": 176537
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 516268,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 15203,
                            "time_enabled": 4872498,
                            "time_running": 4872498,
                            "LLC_MISSES": 36605,
                            "INSTRUCTIONS_RETIRED": 127774
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 199223,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5547,
                            "time_enabled": 8508970,
                            "time_running": 8508970,
                            "LLC_MISSES": 9962,
                            "INSTRUCTIONS_RETIRED": 47600
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 94018,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2828,
                            "time_enabled": 1329619,
                            "time_running": 1329619,
                            "LLC_MISSES": 6876,
                            "INSTRUCTIONS_RETIRED": 18503
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3031865,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 90168,
                            "time_enabled": 21293293,
                            "time_running": 21293293,
                            "LLC_MISSES": 97640,
                            "INSTRUCTIONS_RETIRED": 2803139
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2079313,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 56843,
                            "time_enabled": 6751450,
                            "time_running": 6751450,
                            "LLC_MISSES": 68206,
                            "INSTRUCTIONS_RETIRED": 697982
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29e7391b52aff60cb36",
            "timestamp": "2021-01-13T09:51:26.647",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 162260,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4880,
                            "time_enabled": 707883,
                            "time_running": 707883,
                            "LLC_MISSES": 6888,
                            "INSTRUCTIONS_RETIRED": 55923
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 27361,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 823,
                            "time_enabled": 485936,
                            "time_running": 485936,
                            "LLC_MISSES": 379,
                            "INSTRUCTIONS_RETIRED": 8881
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 107259,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3225,
                            "time_enabled": 649120,
                            "time_running": 649120,
                            "LLC_MISSES": 3808,
                            "INSTRUCTIONS_RETIRED": 49061
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 81044,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2437,
                            "time_enabled": 503767,
                            "time_running": 503767,
                            "LLC_MISSES": 4173,
                            "INSTRUCTIONS_RETIRED": 22626
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 70787,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2129,
                            "time_enabled": 830871,
                            "time_running": 830871,
                            "LLC_MISSES": 1310,
                            "INSTRUCTIONS_RETIRED": 25469
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 49653,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1493,
                            "time_enabled": 500156,
                            "time_running": 500156,
                            "LLC_MISSES": 588,
                            "INSTRUCTIONS_RETIRED": 15553
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 76683,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2306,
                            "time_enabled": 801543,
                            "time_running": 801543,
                            "LLC_MISSES": 1814,
                            "INSTRUCTIONS_RETIRED": 13294
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29f7391b52aff60cb37",
            "timestamp": "2021-01-13T09:51:27.651",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 411699,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5880,
                            "time_enabled": 2839296,
                            "time_running": 2839296,
                            "LLC_MISSES": 3792,
                            "INSTRUCTIONS_RETIRED": 329591
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3659194,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 97807,
                            "time_enabled": 24525781,
                            "time_running": 24525781,
                            "LLC_MISSES": 45945,
                            "INSTRUCTIONS_RETIRED": 5353565
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 404806,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6387,
                            "time_enabled": 3158295,
                            "time_running": 3158295,
                            "LLC_MISSES": 2986,
                            "INSTRUCTIONS_RETIRED": 371558
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 426179,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8333,
                            "time_enabled": 3173290,
                            "time_running": 3173290,
                            "LLC_MISSES": 3441,
                            "INSTRUCTIONS_RETIRED": 329169
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 548219,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12557,
                            "time_enabled": 2868555,
                            "time_running": 2868555,
                            "LLC_MISSES": 5360,
                            "INSTRUCTIONS_RETIRED": 337637
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1617706,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 16214,
                            "time_enabled": 6060590,
                            "time_running": 6060590,
                            "LLC_MISSES": 18265,
                            "INSTRUCTIONS_RETIRED": 1561733
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29f7391b52aff60cb38",
            "timestamp": "2021-01-13T09:51:27.651",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 4668784640,
                            "time_enabled": 6028271049,
                            "time_running": 6028271049
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 21512767,
                            "APERF": 9963530,
                            "TSC": 2120885512,
                            "time_enabled": 6027965489,
                            "time_running": 6027965489
                        },
                        "4": {
                            "MPERF": 17550127,
                            "APERF": 7501994,
                            "TSC": 2121029180,
                            "time_enabled": 6028045244,
                            "time_running": 6028045244
                        },
                        "5": {
                            "MPERF": 7838733,
                            "APERF": 3490693,
                            "TSC": 2121136918,
                            "time_enabled": 6028107312,
                            "time_running": 6028107312
                        },
                        "6": {
                            "MPERF": 9971163,
                            "APERF": 4418697,
                            "TSC": 2121193564,
                            "time_enabled": 6028138771,
                            "time_running": 6028138771
                        },
                        "7": {
                            "MPERF": 8953596,
                            "APERF": 4008079,
                            "TSC": 2121295038,
                            "time_enabled": 6028165743,
                            "time_running": 6028165743
                        },
                        "0": {
                            "MPERF": 19235321,
                            "APERF": 8334032,
                            "TSC": 2121337038,
                            "time_enabled": 6028186350,
                            "time_running": 6028186350
                        },
                        "1": {
                            "MPERF": 15680952,
                            "APERF": 8920447,
                            "TSC": 2121365856,
                            "time_enabled": 6028167115,
                            "time_running": 6028167115
                        },
                        "2": {
                            "MPERF": 11728512,
                            "APERF": 5037841,
                            "TSC": 2121491100,
                            "time_enabled": 6028236214,
                            "time_running": 6028236214
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29f7391b52aff60cb39",
            "timestamp": "2021-01-13T09:51:27.651",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 455651,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12179,
                            "time_enabled": 4641723,
                            "time_running": 4641723,
                            "LLC_MISSES": 26891,
                            "INSTRUCTIONS_RETIRED": 142760
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 737283,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 20142,
                            "time_enabled": 5955670,
                            "time_running": 5955670,
                            "LLC_MISSES": 49963,
                            "INSTRUCTIONS_RETIRED": 247454
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 327642,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8351,
                            "time_enabled": 9025292,
                            "time_running": 9025292,
                            "LLC_MISSES": 18433,
                            "INSTRUCTIONS_RETIRED": 83995
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 108257,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2894,
                            "time_enabled": 1492652,
                            "time_running": 1492652,
                            "LLC_MISSES": 8367,
                            "INSTRUCTIONS_RETIRED": 24246
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2610831,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 69785,
                            "time_enabled": 24243365,
                            "time_running": 24243365,
                            "LLC_MISSES": 72711,
                            "INSTRUCTIONS_RETIRED": 2688596
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2391418,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 38117,
                            "time_enabled": 8656617,
                            "time_running": 8656617,
                            "LLC_MISSES": 95952,
                            "INSTRUCTIONS_RETIRED": 790825
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec29f7391b52aff60cb3a",
            "timestamp": "2021-01-13T09:51:27.651",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 167594,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4480,
                            "time_enabled": 942171,
                            "time_running": 942171,
                            "LLC_MISSES": 8714,
                            "INSTRUCTIONS_RETIRED": 59580
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 485936,
                            "time_running": 485936,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 106762,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2854,
                            "time_enabled": 805628,
                            "time_running": 805628,
                            "LLC_MISSES": 4382,
                            "INSTRUCTIONS_RETIRED": 36800
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 503767,
                            "time_running": 503767,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 87920,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2349,
                            "time_enabled": 983449,
                            "time_running": 983449,
                            "LLC_MISSES": 2675,
                            "INSTRUCTIONS_RETIRED": 33336
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 69889,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1869,
                            "time_enabled": 612140,
                            "time_running": 612140,
                            "LLC_MISSES": 1562,
                            "INSTRUCTIONS_RETIRED": 24311
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 97861,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2615,
                            "time_enabled": 928918,
                            "time_running": 928918,
                            "LLC_MISSES": 2543,
                            "INSTRUCTIONS_RETIRED": 20227
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a07391b52aff60cb3b",
            "timestamp": "2021-01-13T09:51:28.655",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 569119,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12188,
                            "time_enabled": 3366388,
                            "time_running": 3366388,
                            "LLC_MISSES": 5582,
                            "INSTRUCTIONS_RETIRED": 399814
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3761509,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 75305,
                            "time_enabled": 27706920,
                            "time_running": 27706920,
                            "LLC_MISSES": 52410,
                            "INSTRUCTIONS_RETIRED": 5404980
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 490041,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10600,
                            "time_enabled": 3640050,
                            "time_running": 3640050,
                            "LLC_MISSES": 3629,
                            "INSTRUCTIONS_RETIRED": 289430
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 423751,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 7394,
                            "time_enabled": 3501595,
                            "time_running": 3501595,
                            "LLC_MISSES": 3212,
                            "INSTRUCTIONS_RETIRED": 333900
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 596217,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8050,
                            "time_enabled": 3219269,
                            "time_running": 3219269,
                            "LLC_MISSES": 5347,
                            "INSTRUCTIONS_RETIRED": 330330
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1816936,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 48564,
                            "time_enabled": 8168434,
                            "time_running": 8168434,
                            "LLC_MISSES": 17794,
                            "INSTRUCTIONS_RETIRED": 1585502
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a07391b52aff60cb3c",
            "timestamp": "2021-01-13T09:51:28.655",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5001969664,
                            "time_enabled": 7031400476,
                            "time_running": 7031400476
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 8099760,
                            "APERF": 3505139,
                            "TSC": 2119146866,
                            "time_enabled": 7031365787,
                            "time_running": 7031365787
                        },
                        "4": {
                            "MPERF": 16190842,
                            "APERF": 8183625,
                            "TSC": 2119012126,
                            "time_enabled": 7031378350,
                            "time_running": 7031378350
                        },
                        "5": {
                            "MPERF": 25725088,
                            "APERF": 11165367,
                            "TSC": 2118952466,
                            "time_enabled": 7031409958,
                            "time_running": 7031409958
                        },
                        "6": {
                            "MPERF": 8796165,
                            "APERF": 3930283,
                            "TSC": 2118938020,
                            "time_enabled": 7031435013,
                            "time_running": 7031435013
                        },
                        "7": {
                            "MPERF": 57954577,
                            "APERF": 25647574,
                            "TSC": 2118836142,
                            "time_enabled": 7031414057,
                            "time_running": 7031414057
                        },
                        "0": {
                            "MPERF": 26296973,
                            "APERF": 11904017,
                            "TSC": 2118809328,
                            "time_enabled": 7031416070,
                            "time_running": 7031416070
                        },
                        "1": {
                            "MPERF": 24694557,
                            "APERF": 10489452,
                            "TSC": 2118763706,
                            "time_enabled": 7031378601,
                            "time_running": 7031378601
                        },
                        "2": {
                            "MPERF": 14806090,
                            "APERF": 6372424,
                            "TSC": 2118643952,
                            "time_enabled": 7031393141,
                            "time_running": 7031393141
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a07391b52aff60cb3d",
            "timestamp": "2021-01-13T09:51:28.655",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 261884,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5551,
                            "time_enabled": 4950938,
                            "time_running": 4950938,
                            "LLC_MISSES": 16007,
                            "INSTRUCTIONS_RETIRED": 59430
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 473828,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12667,
                            "time_enabled": 6735934,
                            "time_running": 6735934,
                            "LLC_MISSES": 33427,
                            "INSTRUCTIONS_RETIRED": 113206
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 244839,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6545,
                            "time_enabled": 9422618,
                            "time_running": 9422618,
                            "LLC_MISSES": 15510,
                            "INSTRUCTIONS_RETIRED": 63143
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 93578,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2502,
                            "time_enabled": 1639007,
                            "time_running": 1639007,
                            "LLC_MISSES": 7417,
                            "INSTRUCTIONS_RETIRED": 18549
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2557091,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 68349,
                            "time_enabled": 27133716,
                            "time_running": 27133716,
                            "LLC_MISSES": 72801,
                            "INSTRUCTIONS_RETIRED": 2688754
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2418610,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 64647,
                            "time_enabled": 11712382,
                            "time_running": 11712382,
                            "LLC_MISSES": 93658,
                            "INSTRUCTIONS_RETIRED": 794063
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a07391b52aff60cb3e",
            "timestamp": "2021-01-13T09:51:28.655",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 139954,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3741,
                            "time_enabled": 1141370,
                            "time_running": 1141370,
                            "LLC_MISSES": 3988,
                            "INSTRUCTIONS_RETIRED": 36395
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 142021,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3796,
                            "time_enabled": 236782,
                            "time_running": 236782,
                            "LLC_MISSES": 3167,
                            "INSTRUCTIONS_RETIRED": 49092
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 84182,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2250,
                            "time_enabled": 631036,
                            "time_running": 631036,
                            "LLC_MISSES": 2806,
                            "INSTRUCTIONS_RETIRED": 30252
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 70698,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1889,
                            "time_enabled": 902565,
                            "time_running": 902565,
                            "LLC_MISSES": 3273,
                            "INSTRUCTIONS_RETIRED": 28015
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 68210,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1823,
                            "time_enabled": 598878,
                            "time_running": 598878,
                            "LLC_MISSES": 4413,
                            "INSTRUCTIONS_RETIRED": 22646
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 109945,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2939,
                            "time_enabled": 1201624,
                            "time_running": 1201624,
                            "LLC_MISSES": 1778,
                            "INSTRUCTIONS_RETIRED": 37506
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 23888,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 639,
                            "time_enabled": 665268,
                            "time_running": 665268,
                            "LLC_MISSES": 290,
                            "INSTRUCTIONS_RETIRED": 6016
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 83052,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2220,
                            "time_enabled": 1040303,
                            "time_running": 1040303,
                            "LLC_MISSES": 3729,
                            "INSTRUCTIONS_RETIRED": 24514
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a17391b52aff60cb3f",
            "timestamp": "2021-01-13T09:51:29.659",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 40823,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1091,
                            "time_enabled": 1204376,
                            "time_running": 1204376,
                            "LLC_MISSES": 617,
                            "INSTRUCTIONS_RETIRED": 12843
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 198646,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5309,
                            "time_enabled": 518377,
                            "time_running": 518377,
                            "LLC_MISSES": 7340,
                            "INSTRUCTIONS_RETIRED": 71732
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 55078,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1473,
                            "time_enabled": 731057,
                            "time_running": 731057,
                            "LLC_MISSES": 893,
                            "INSTRUCTIONS_RETIRED": 17820
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 88162,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2356,
                            "time_enabled": 1034982,
                            "time_running": 1034982,
                            "LLC_MISSES": 2887,
                            "INSTRUCTIONS_RETIRED": 32403
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 598878,
                            "time_running": 598878,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 119573,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3197,
                            "time_enabled": 1429800,
                            "time_running": 1429800,
                            "LLC_MISSES": 1971,
                            "INSTRUCTIONS_RETIRED": 37671
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 83297,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2227,
                            "time_enabled": 813514,
                            "time_running": 813514,
                            "LLC_MISSES": 1558,
                            "INSTRUCTIONS_RETIRED": 33973
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 229413,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6132,
                            "time_enabled": 1352596,
                            "time_running": 1352596,
                            "LLC_MISSES": 12698,
                            "INSTRUCTIONS_RETIRED": 77359
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a17391b52aff60cb40",
            "timestamp": "2021-01-13T09:51:29.659",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 441545,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12108,
                            "time_enabled": 5542705,
                            "time_running": 5542705,
                            "LLC_MISSES": 30280,
                            "INSTRUCTIONS_RETIRED": 130752
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 544605,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 14534,
                            "time_enabled": 7587174,
                            "time_running": 7587174,
                            "LLC_MISSES": 33976,
                            "INSTRUCTIONS_RETIRED": 153269
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 222448,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5481,
                            "time_enabled": 9757768,
                            "time_running": 9757768,
                            "LLC_MISSES": 9910,
                            "INSTRUCTIONS_RETIRED": 62712
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 90701,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2601,
                            "time_enabled": 1791657,
                            "time_running": 1791657,
                            "LLC_MISSES": 5958,
                            "INSTRUCTIONS_RETIRED": 18587
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 8808400,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 235571,
                            "time_enabled": 37014501,
                            "time_running": 37014501,
                            "LLC_MISSES": 127670,
                            "INSTRUCTIONS_RETIRED": 9443782
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2385827,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 38313,
                            "time_enabled": 13632189,
                            "time_running": 13632189,
                            "LLC_MISSES": 91483,
                            "INSTRUCTIONS_RETIRED": 780872
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a17391b52aff60cb41",
            "timestamp": "2021-01-13T09:51:29.659",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 408665,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5729,
                            "time_enabled": 3625638,
                            "time_running": 3625638,
                            "LLC_MISSES": 3216,
                            "INSTRUCTIONS_RETIRED": 327760
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3692929,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 104007,
                            "time_enabled": 32101540,
                            "time_running": 32101540,
                            "LLC_MISSES": 48409,
                            "INSTRUCTIONS_RETIRED": 5369378
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 497092,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8999,
                            "time_enabled": 4029609,
                            "time_running": 4029609,
                            "LLC_MISSES": 4408,
                            "INSTRUCTIONS_RETIRED": 406815
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 492713,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10435,
                            "time_enabled": 3957613,
                            "time_running": 3957613,
                            "LLC_MISSES": 3450,
                            "INSTRUCTIONS_RETIRED": 432232
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 570969,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 13447,
                            "time_enabled": 3799664,
                            "time_running": 3799664,
                            "LLC_MISSES": 6375,
                            "INSTRUCTIONS_RETIRED": 351036
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1654852,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 16710,
                            "time_enabled": 8912512,
                            "time_running": 8912512,
                            "LLC_MISSES": 18023,
                            "INSTRUCTIONS_RETIRED": 1562854
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a17391b52aff60cb42",
            "timestamp": "2021-01-13T09:51:29.659",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5327028224,
                            "time_enabled": 8036558740,
                            "time_running": 8036558740
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 8801509,
                            "APERF": 4568139,
                            "TSC": 2122076126,
                            "time_enabled": 8036142774,
                            "time_running": 8036142774
                        },
                        "4": {
                            "MPERF": 27404227,
                            "APERF": 11334400,
                            "TSC": 2122156102,
                            "time_enabled": 8036192504,
                            "time_running": 8036192504
                        },
                        "5": {
                            "MPERF": 19476024,
                            "APERF": 8519458,
                            "TSC": 2122181926,
                            "time_enabled": 8036234858,
                            "time_running": 8036234858
                        },
                        "6": {
                            "MPERF": 18199031,
                            "APERF": 7589800,
                            "TSC": 2122318632,
                            "time_enabled": 8036324614,
                            "time_running": 8036324614
                        },
                        "7": {
                            "MPERF": 25177650,
                            "APERF": 10742207,
                            "TSC": 2122561468,
                            "time_enabled": 8036422662,
                            "time_running": 8036422662
                        },
                        "0": {
                            "MPERF": 36768541,
                            "APERF": 15737436,
                            "TSC": 2122613324,
                            "time_enabled": 8036444786,
                            "time_running": 8036444786
                        },
                        "1": {
                            "MPERF": 26504881,
                            "APERF": 13334020,
                            "TSC": 2122643416,
                            "time_enabled": 8036425094,
                            "time_running": 8036425094
                        },
                        "2": {
                            "MPERF": 17004139,
                            "APERF": 7107468,
                            "TSC": 2122773564,
                            "time_enabled": 8036498827,
                            "time_running": 8036498827
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a27391b52aff60cb43",
            "timestamp": "2021-01-13T09:51:30.663",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 336588,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8996,
                            "time_enabled": 6004389,
                            "time_running": 6004389,
                            "LLC_MISSES": 25768,
                            "INSTRUCTIONS_RETIRED": 90802
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 463995,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12634,
                            "time_enabled": 8390971,
                            "time_running": 8390971,
                            "LLC_MISSES": 32740,
                            "INSTRUCTIONS_RETIRED": 113476
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 181483,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4391,
                            "time_enabled": 10042331,
                            "time_running": 10042331,
                            "LLC_MISSES": 7060,
                            "INSTRUCTIONS_RETIRED": 47608
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 105142,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2114,
                            "time_enabled": 1926325,
                            "time_running": 1926325,
                            "LLC_MISSES": 7116,
                            "INSTRUCTIONS_RETIRED": 18487
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2582351,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 69156,
                            "time_enabled": 39937449,
                            "time_running": 39937449,
                            "LLC_MISSES": 69912,
                            "INSTRUCTIONS_RETIRED": 2679605
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2370902,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 38231,
                            "time_enabled": 15561437,
                            "time_running": 15561437,
                            "LLC_MISSES": 94538,
                            "INSTRUCTIONS_RETIRED": 781321
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a27391b52aff60cb44",
            "timestamp": "2021-01-13T09:51:30.663",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 483867,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 11137,
                            "time_enabled": 4115919,
                            "time_running": 4115919,
                            "LLC_MISSES": 3496,
                            "INSTRUCTIONS_RETIRED": 336610
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3700022,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 78910,
                            "time_enabled": 35432562,
                            "time_running": 35432562,
                            "LLC_MISSES": 49261,
                            "INSTRUCTIONS_RETIRED": 5387404
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 381981,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 7369,
                            "time_enabled": 4354110,
                            "time_running": 4354110,
                            "LLC_MISSES": 3152,
                            "INSTRUCTIONS_RETIRED": 286087
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 307032,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 4562,
                            "time_enabled": 4164733,
                            "time_running": 4164733,
                            "LLC_MISSES": 2338,
                            "INSTRUCTIONS_RETIRED": 250290
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 607601,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 8418,
                            "time_enabled": 4181817,
                            "time_running": 4181817,
                            "LLC_MISSES": 6881,
                            "INSTRUCTIONS_RETIRED": 357795
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1728255,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 19118,
                            "time_enabled": 9754030,
                            "time_running": 9754030,
                            "LLC_MISSES": 19108,
                            "INSTRUCTIONS_RETIRED": 1625964
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a27391b52aff60cb45",
            "timestamp": "2021-01-13T09:51:30.663",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 105539,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2821,
                            "time_enabled": 1356043,
                            "time_running": 1356043,
                            "LLC_MISSES": 4926,
                            "INSTRUCTIONS_RETIRED": 35879
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 6118999,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 163553,
                            "time_enabled": 7436723,
                            "time_running": 7436723,
                            "LLC_MISSES": 87505,
                            "INSTRUCTIONS_RETIRED": 9678168
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 25173,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 673,
                            "time_enabled": 778682,
                            "time_running": 778682,
                            "LLC_MISSES": 260,
                            "INSTRUCTIONS_RETIRED": 9143
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 144804,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3868,
                            "time_enabled": 1276073,
                            "time_running": 1276073,
                            "LLC_MISSES": 2197,
                            "INSTRUCTIONS_RETIRED": 73502
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 104463,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2792,
                            "time_enabled": 789784,
                            "time_running": 789784,
                            "LLC_MISSES": 1327,
                            "INSTRUCTIONS_RETIRED": 39201
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 686817,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 18353,
                            "time_enabled": 2984574,
                            "time_running": 2984574,
                            "LLC_MISSES": 4558,
                            "INSTRUCTIONS_RETIRED": 408005
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 132271,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 3534,
                            "time_enabled": 1023170,
                            "time_running": 1023170,
                            "LLC_MISSES": 1067,
                            "INSTRUCTIONS_RETIRED": 57130
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 104732,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2799,
                            "time_enabled": 1501725,
                            "time_running": 1501725,
                            "LLC_MISSES": 2575,
                            "INSTRUCTIONS_RETIRED": 37650
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a27391b52aff60cb46",
            "timestamp": "2021-01-13T09:51:30.663",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5543297024,
                            "time_enabled": 9039792060,
                            "time_running": 9039792060
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 39220264,
                            "APERF": 17333980,
                            "TSC": 2119589066,
                            "time_enabled": 9039750647,
                            "time_running": 9039750647
                        },
                        "4": {
                            "MPERF": 34853992,
                            "APERF": 15737574,
                            "TSC": 2119516288,
                            "time_enabled": 9039763850,
                            "time_running": 9039763850
                        },
                        "5": {
                            "MPERF": 7733756,
                            "APERF": 3337465,
                            "TSC": 2119457312,
                            "time_enabled": 9039776088,
                            "time_running": 9039776088
                        },
                        "6": {
                            "MPERF": 7321180,
                            "APERF": 3246242,
                            "TSC": 2119279802,
                            "time_enabled": 9039781172,
                            "time_running": 9039781172
                        },
                        "7": {
                            "MPERF": 9687723,
                            "APERF": 4316597,
                            "TSC": 2119050564,
                            "time_enabled": 9039776220,
                            "time_running": 9039776220
                        },
                        "0": {
                            "MPERF": 52695581,
                            "APERF": 22789780,
                            "TSC": 2119067104,
                            "time_enabled": 9039796892,
                            "time_running": 9039796892
                        },
                        "1": {
                            "MPERF": 15346965,
                            "APERF": 8695619,
                            "TSC": 2118959092,
                            "time_enabled": 9039765674,
                            "time_running": 9039765674
                        },
                        "2": {
                            "MPERF": 19129363,
                            "APERF": 8139082,
                            "TSC": 2118895752,
                            "time_enabled": 9039777139,
                            "time_running": 9039777139
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a37391b52aff60cb47",
            "timestamp": "2021-01-13T09:51:31.667",
            "sensor": "sensor_test",
            "target": "powerapi-sensor",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 438089,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 6153,
                            "time_enabled": 4393136,
                            "time_running": 4393136,
                            "LLC_MISSES": 3992,
                            "INSTRUCTIONS_RETIRED": 331953
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 3656143,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 97724,
                            "time_enabled": 39535039,
                            "time_running": 39535039,
                            "LLC_MISSES": 51183,
                            "INSTRUCTIONS_RETIRED": 5329003
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 376556,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5713,
                            "time_enabled": 4626849,
                            "time_running": 4626849,
                            "LLC_MISSES": 2607,
                            "INSTRUCTIONS_RETIRED": 287565
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 457132,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 9413,
                            "time_enabled": 4576889,
                            "time_running": 4576889,
                            "LLC_MISSES": 4132,
                            "INSTRUCTIONS_RETIRED": 309263
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 597726,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 12990,
                            "time_enabled": 4746140,
                            "time_running": 4746140,
                            "LLC_MISSES": 4998,
                            "INSTRUCTIONS_RETIRED": 287484
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 1650168,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 16539,
                            "time_enabled": 10471431,
                            "time_running": 10471431,
                            "LLC_MISSES": 18558,
                            "INSTRUCTIONS_RETIRED": 1583651
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a37391b52aff60cb48",
            "timestamp": "2021-01-13T09:51:31.667",
            "sensor": "sensor_test",
            "target": "mongo",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 393745,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 10748,
                            "time_enabled": 6535441,
                            "time_running": 6535441,
                            "LLC_MISSES": 27780,
                            "INSTRUCTIONS_RETIRED": 113132
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 528746,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 14613,
                            "time_enabled": 9252237,
                            "time_running": 9252237,
                            "LLC_MISSES": 37491,
                            "INSTRUCTIONS_RETIRED": 146094
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 283324,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 7218,
                            "time_enabled": 10507182,
                            "time_running": 10507182,
                            "LLC_MISSES": 13638,
                            "INSTRUCTIONS_RETIRED": 71098
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 203485,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 5678,
                            "time_enabled": 2245585,
                            "time_running": 2245585,
                            "LLC_MISSES": 14538,
                            "INSTRUCTIONS_RETIRED": 56391
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2606316,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 77234,
                            "time_enabled": 43214790,
                            "time_running": 43214790,
                            "LLC_MISSES": 72160,
                            "INSTRUCTIONS_RETIRED": 2686541
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 2268782,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 35813,
                            "time_enabled": 17363245,
                            "time_running": 17363245,
                            "LLC_MISSES": 85100,
                            "INSTRUCTIONS_RETIRED": 756879
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 0,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 0,
                            "time_enabled": 0,
                            "time_running": 0,
                            "LLC_MISSES": 0,
                            "INSTRUCTIONS_RETIRED": 0
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a37391b52aff60cb49",
            "timestamp": "2021-01-13T09:51:31.667",
            "sensor": "sensor_test",
            "target": "all",
            "groups": {
                "rapl": {
                    "0": {
                        "7": {
                            "RAPL_ENERGY_PKG": 5154537472,
                            "time_enabled": 10044542573,
                            "time_running": 10044542573
                        }
                    }
                },
                "msr": {
                    "0": {
                        "3": {
                            "MPERF": 8312740,
                            "APERF": 4225223,
                            "TSC": 2121288728,
                            "time_enabled": 10044155010,
                            "time_running": 10044155010
                        },
                        "4": {
                            "MPERF": 18022984,
                            "APERF": 7606957,
                            "TSC": 2121358412,
                            "time_enabled": 10044200483,
                            "time_running": 10044200483
                        },
                        "5": {
                            "MPERF": 9505487,
                            "APERF": 4215280,
                            "TSC": 2121625954,
                            "time_enabled": 10044338222,
                            "time_running": 10044338222
                        },
                        "6": {
                            "MPERF": 20078144,
                            "APERF": 8798598,
                            "TSC": 2121738302,
                            "time_enabled": 10044397881,
                            "time_running": 10044397881
                        },
                        "7": {
                            "MPERF": 6202826,
                            "APERF": 2765288,
                            "TSC": 2121815288,
                            "time_enabled": 10044427306,
                            "time_running": 10044427306
                        },
                        "0": {
                            "MPERF": 23940911,
                            "APERF": 10069087,
                            "TSC": 2121866896,
                            "time_enabled": 10044471545,
                            "time_running": 10044471545
                        },
                        "1": {
                            "MPERF": 13001023,
                            "APERF": 7632761,
                            "TSC": 2121924996,
                            "time_enabled": 10044468140,
                            "time_running": 10044468140
                        },
                        "2": {
                            "MPERF": 13357998,
                            "APERF": 5500788,
                            "TSC": 2121987988,
                            "time_enabled": 10044511256,
                            "time_running": 10044511256
                        }
                    }
                }
            }
        },
        {
            "_id": "5ffec2a37391b52aff60cb4a",
            "timestamp": "2021-01-13T09:51:31.667",
            "sensor": "sensor_test",
            "target": "influxdb",
            "groups": {
                "core": {
                    "0": {
                        "3": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 76434,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2298,
                            "time_enabled": 1473505,
                            "time_running": 1473505,
                            "LLC_MISSES": 2958,
                            "INSTRUCTIONS_RETIRED": 22666
                        },
                        "4": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 103894,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2777,
                            "time_enabled": 7568851,
                            "time_running": 7568851,
                            "LLC_MISSES": 3893,
                            "INSTRUCTIONS_RETIRED": 32743
                        },
                        "5": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 57616,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1625,
                            "time_enabled": 886416,
                            "time_running": 886416,
                            "LLC_MISSES": 696,
                            "INSTRUCTIONS_RETIRED": 18016
                        },
                        "6": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 43921,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 1245,
                            "time_enabled": 1364101,
                            "time_running": 1364101,
                            "LLC_MISSES": 680,
                            "INSTRUCTIONS_RETIRED": 12116
                        },
                        "7": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 81582,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2454,
                            "time_enabled": 912992,
                            "time_running": 912992,
                            "LLC_MISSES": 3528,
                            "INSTRUCTIONS_RETIRED": 41180
                        },
                        "0": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 81410,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2295,
                            "time_enabled": 3153354,
                            "time_running": 3153354,
                            "LLC_MISSES": 1183,
                            "INSTRUCTIONS_RETIRED": 37698
                        },
                        "1": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 25521,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 767,
                            "time_enabled": 1079332,
                            "time_running": 1079332,
                            "LLC_MISSES": 364,
                            "INSTRUCTIONS_RETIRED": 6075
                        },
                        "2": {
                            "CPU_CLK_THREAD_UNHALTED:THREAD_P": 66682,
                            "CPU_CLK_THREAD_UNHALTED:REF_P": 2005,
                            "time_enabled": 1606596,
                            "time_running": 1606596,
                            "LLC_MISSES": 2219,
                            "INSTRUCTIONS_RETIRED": 13328
                        }
                    }
                }
            }
        }
    ]
