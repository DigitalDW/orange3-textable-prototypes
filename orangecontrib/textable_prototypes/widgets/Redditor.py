"""
Class Redditor
Copyright 2019 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable-Prototypes package.

Orange3-Textable-Prototypes is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable-Prototypes is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes. If not, see
<http://www.gnu.org/licenses/>.
"""

__version__ = u"0.0.1"
__author__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__maintainer__ = "Nahuel Degonda, Olivia Edelman, Loris Rimaz"
__email__ = "nahuel.degonda@unil.ch, olivia.edelman@unil.ch, loris.rimaz@unil.ch"

# Standard imports...
import praw
import prawcore

from Orange.widgets import widget, gui
from Orange.widgets.settings import Setting

from _textable.widgets.TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, pluralize,
    InfoBox, SendButton, ProgressBar
)

from LTTL.Segmentation import Segmentation
import LTTL.Segmenter as Segmenter
from LTTL.Segment import Segment
from LTTL.Input import Input

class Redditor(OWTextableBaseWidget):
    """An Orange widget to scrape Reddit"""

    #----------------------------------------------------------------------
    # Widget's metadata...

    name = "Redditor"
    description = "Scrap on Reddit"
    icon = "icons/mywidget.svg"
    priority = 20

    #----------------------------------------------------------------------
    # Channel definitions...

    # inputs = []
    outputs = [("Segmentation", Segmentation)]

    #----------------------------------------------------------------------
    # GUI layout parameters...

    want_main_area = False
    resizing_enabled = True

    # Settings
    mode = Setting("Subreddit")
    subreddit = Setting(u'')
    URL = Setting(u'')
    fullText = Setting(u'')

    # Praw instance
    reddit = praw.Reddit(
        client_id="aHeP3Ub7aILvsg",
        client_secret=None,
        username="RedditorApp",
        password="RedditorProg2019",
        user_agent="Redditor by /u/RedditorApp"
    )

    # Segment list
    segments = list()

    def __init__(self):
        super().__init__()

        #----------------------------------------------------------------------
        # User interface...
        self.infoBox = InfoBox(
            widget=self.controlArea,
        )

        sourceBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Source',
            orientation='vertical',
            addSpace=False,
        )

        self.choiceBox = gui.comboBox(
            widget=sourceBox,
            master=self, 
            value='mode', 
            label="Mode:",
            callback=self.mode_changed,
            tooltip= "Chose mode",
            orientation='horizontal',
            sendSelectedValue=True,
            items=["Subreddit", "URL", "Full text"],
        )

        self.modeBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        """
        modeRadio = gui.radioButtons(
            widget=self.modeBox,
            master=self,
            value='mode',
            label="Mode",
            orientation='horizontal',
            callback=self.mode_changed,
            btnLabels=["SubReddit", "Post"],
        )
        """

        self.urlBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        urlPath = gui.lineEdit(
            widget=self.urlBox,
            master=self,
            value='URL',
            orientation='horizontal',
            label=u'URL:',
            labelWidth=101
        )

        self.subredditBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )

        subredditName = gui.lineEdit(
            widget=self.subredditBox,
            master=self,
            value='subreddit',
            orientation='horizontal',
            label=u'reddit.com/r/...:',
            labelWidth=101
        
        )
        self.fullTextBox = gui.widgetBox(
            widget=sourceBox,
            orientation='horizontal',
            addSpace=False,
        )
        
        fullText = gui.lineEdit(
            widget=self.fullTextBox,
            master=self,
            value='fullText',
            orientation='horizontal',
            label=u'search all reddit',
            labelWidth=101
        )
        '''
        self.fetchButton = gui.button(
            widget=sourceBox,
            master=self,
            label=u'Get content',
            callback=self.get_content,
        )

        '''
        self.sendBox = gui.widgetBox(
            widget=self.controlArea,
            orientation='vertical',
            addSpace=False,
        )

        self.sendButton = SendButton(
            widget=self.sendBox,
            master=self,
            callback=self.get_content,
            infoBoxAttribute='infoBox',

        )
        

        self.label = gui.widgetLabel(self.controlArea, "Chose a mode")

        # Send button...
        #self.sendButton.draw()

        # Info box...
        self.infoBox.draw()
        self.sendButton.draw()

        self.mode_changed()

    def mode_changed(self):
        """Reimplemented from OWWidget."""
        if self.mode == "Subreddit": # 0 = subreddit selected
            # cacher URL
            self.urlBox.setVisible(False)
            # montrer subreddit
            self.subredditBox.setVisible(True)
        elif self.mode == "URL": # self.mode ==1 => post selected
            # cacher subreddit
            self.subredditBox.setVisible(False)

            # montrer URL
            self.urlBox.setVisible(True)
        elif self.mode == "Full text":
            # cacher subreddit
            self.subredditBox.setVisible(False)

            # montrer URL
            self.urlBox.setVisible(True)

        self.label.setText("Mode is: %s" % self.mode)
        # Clear the channel by sending None.
        self.send("Segmentation", None)
    """
    def update_send_button(self):
        # self.mode == 0 => subreddit selected, self.mode == 1 => post selected
        if ((self.mode == "Subreddit" and len(self.subreddit) > 0) or
            (self.mode == "URL" and len(self.URL) > 0) or
            (self.mode == "Full text" and len(self.URL) > 0)):
            self.sendButton.setDisabled(False)
        else:
            self.sendButton.setDisabled(True)
    """
    def get_content(self):
        self.label.setText('Getting content...')
        print(self.reddit.user.me())

        # Differenciate method depending of user selection
        if self.mode == "Subreddit":
            # Get the subreddit based on subreddit name
            try:
                subreddit = self.reddit.subreddit(self.subreddit)
                # Get 1st "hot" post
                posts = subreddit.hot(limit=1)
                # Loop on the posts found
                for post in posts:
                    self.get_post_data(post)
                    self.get_comment_content(post)
                self.label.setText('Content found !')
            except prawcore.exceptions.Redirect:
                self.label.setText('Error: subreddit not found !')
            except prawcore.exceptions.NotFound:
                self.label.setText('Error: subreddit not found !')
        elif self.mode == "URL":
            # Get post based on URL
            try:
                post = self.reddit.submission(url=self.URL)
                self.get_post_data(post)
                self.get_comment_content(post)
                self.label.setText('Content found !')
            except prawcore.exceptions.NotFound:
                self.label.setText('Error: no match for URL')
            except praw.exceptions.ClientException:
                self.label.setText('Error: Invalid URL !')
        elif self.mode == "Full text":
            reddit = self.reddit.subreddit("all")
            for post in reddit.search("yellow car", sort="relevance", limit=1):
                self.get_post_data(post)
                self.get_comment_content(post)
                print(post.title)
            self.label.setText('Content found !')

        self.send("Segmentation", Segmentation(self.segments))
        self.segments = []

    def get_post_data(self, post):
        annotations = dict()
        annotations["Title"] = post.title
        annotations["Id"] = post.id
        text = Input(post.selftext)

        self.segments.append(
            Segment(
                str_index=text[0].str_index,
                start=text[0].start,
                end=text[0].end,
                annotations=annotations
            )
        )
    
    def get_comment_content(self, post):
        post.comments.replace_more(limit=0)
        comments = post.comments.list()

        for comment in comments:
            annotations = dict()
            annotations["Title"] = post.title
            annotations["Id"] = comment.id
            annotations["Parent"] = comment.parent_id

            text = Input(comment.body)

            self.segments.append(
                Segment(
                    str_index=text[0].str_index,
                    start=text[0].start,
                    end=text[0].end,
                    annotations=annotations
                )
            )

    """
    def send_data(self):
        self.label.setText("Envoyé! Mode is: {}".format(self.mode))
    """


 
# The following code lets you execute the code outside of Orange (to view the
# resulting interface)...
if __name__ == "__main__":
    from PyQt4.QtGui import QApplication
    import sys
    my_app = QApplication(list(sys.argv))
    my_widget = Redditor()
    my_widget.show()
    my_widget.raise_()
    my_app.exec_()
    my_widget.saveSettings()


