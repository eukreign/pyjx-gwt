# Copyright 2006 James Tauber and contributors
# Copyright (C) 2009 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from html5 import DOM
from html5 import Factory

from gwt.SimplePanel import SimplePanel
from gwt.Focus import FocusMixin
from gwt import Focus

from gwt.ClickListener import ClickHandler
from gwt.KeyboardListener import KeyboardHandler
from gwt.FocusListener import FocusHandler
from gwt.MouseListener import MouseHandler

class FocusPanel(SimplePanel, FocusHandler, KeyboardHandler,
                          MouseHandler, ClickHandler,
                          FocusMixin):

    def __init__(self, **kwargs):
        """ pass in Widget={the widget} so that Applier will call setWidget.
        """

        SimplePanel.__init__(self, Focus.createFocusable(), **kwargs)
        FocusHandler.__init__(self)
        KeyboardHandler.__init__(self)
        ClickHandler.__init__(self)
        MouseHandler.__init__(self)

Factory.registerClass('gwt.FocusPanel', 'FocusPanel', FocusPanel)
