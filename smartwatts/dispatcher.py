# Copyright (C) 2021  INRIA
# Copyright (C) 2021  University of Lille
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from thespian.actors import ChildActorExited, ActorAddress

from powerapi.dispatcher import DispatcherActor
from powerapi.message import EndMessage


class SmartwattsDispatcherActor(DispatcherActor):
    """
    Dispatcher Actor that use formula pusher and power pusher
    """
    def receiveMsg_ChildActorExited(self, message: ChildActorExited, sender: ActorAddress):
        DispatcherActor.receiveMsg_ChildActorExited(self, message, sender)
        if self._exit_mode and not self.formula_pool:
            for _, pusher in self.formula_values.pushers.items():
                self.send(pusher, EndMessage(self.name))
