import kivy

kivy.require('1.10.1')

import datetime
import time
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.storage.jsonstore import JsonStore
import json
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import *


# The Streak itself ;)
class Streak():
    def __init__(self, action, delay, day, hour, minute, score=1, delta=0):
        self.action = action
        self.delay = delay
        self.day = day
        self.hour = hour
        self.minute = minute
        self.score = score
        self.delta = delta


# Self explanitory
class MainScreen(Screen):
    pass


class ScreenOne(Screen):
    pass


class ScreenTwo(Screen):
    pass


class ScreenThree(Screen):
    pass


class ScreenManagement(ScreenManager):
    main_screen = ObjectProperty(None)
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)
    screen_three = ObjectProperty(None)


# Used to connect .kv file and .py file
presentation = Builder.load_file("StreakStar.kv")

# the streak buttons
class StreakButton(Button):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(f"\nStreakButton.on_touch_down: text={self.text}")
            self.dispatch('on_press')
            return True
        return super(StreakButton, self).on_touch_down(touch)


class MainApp(App):
    def build(self):  # build() returns an instance
        self.store = JsonStore("streak.json")  # file that stores the streaks:
        Clock.schedule_interval(self.check_streak, 1/30.) # used to call functions dynamicaly
        Clock.schedule_interval(self.score_gone, 1/30.)
        Clock.schedule_interval(self.update_high, 1/30.)

        return presentation

    # used to see if streak is early, ontime, or late, then changes the color of button
    def check_streak(self, dt):
        for child in reversed(self.root.screen_two.ids.streak_zone.children):
            name = child.id

            with open("streak.json", "r") as read_file:
                data = json.load(read_file)

            for key in data.keys():
                if key == name:
                    delay = data.get(key, {}).get('delay')  # get value of nested key 'delay'
                    self.honey = data[key]['delta']
                    float(self.honey)


                if delay > time.time() < self.honey:  # early (yellow)
                    child.background_normal = ''
                    child.background_color = [1, 1, 0, .95]
                    child.unbind(on_press=self.add_score)
                    child.bind(on_press=self.display_streak)
                    child.bind(on_press=self.early_click)
                    child.unbind(on_press=self.draw_streak)
                    child.unbind(on_press=self.late_click)

                elif delay > time.time() > self.honey:  # on time (green)
                    child.background_normal = ''
                    child.background_color = [0, 1, 0, .95]
                    child.unbind(on_press=self.early_click)
                    child.bind(on_press=self.add_score)
                    child.bind(on_press=self.display_streak)
                    child.bind(on_press=self.draw_streak)
                    child.unbind(on_press=self.late_click)

                elif delay < time.time() > self.honey:  # late (red)
                    child.background_normal = ''
                    child.background_color = [1, 0, 0, .95]
                    child.unbind(on_press=self.add_score)
                    child.bind(on_press=self.display_streak)
                    child.unbind(on_press=self.early_click)
                    child.unbind(on_press=self.draw_streak)
                    child.bind(on_press=self.late_click)

    # when button is early or yellow
    def early_click(self, obj):
        early_text = ("you're too early wait %s minute(s)" % (round((self.honey - time.time()) / 60)))
        pop_early = Popup(title="Early!", content=Label(text=early_text),
                          size_hint=(None, None), size=(300, 100))
        pop_early.open()

    # when button is late or red
    def late_click(self, obj):
        late_text = "Its too late, delete streak and start over :("
        pop_late = Popup(title="Late!", content=Label(text=late_text),
                        size_hint=(None, None      ), size=(300,300))

        pop_late.open()
        self.third_screen()

    # displays third screen
    def third_screen(self, *args):
        self.root.current = 'three'

    # displays second screen and buttons
    def change_screen(self, *args):
        self.root.current = 'two'

    # clears page of all widgets
    def restart(self):
        self.root.screen_two.ids.streak_zone.clear_widgets()
        self.root.screen_two.ids.high_label.clear_widgets()

    # display the names of the streaks in a list on PageTwo
    def display_btn(self):
        no_data = "You have no stored streaks!"
        popup_2 = Popup(title="No Streaks!", content=Label(text=no_data),
                        size_hint=(None, None), size=(300, 100))

        try:
            with open("streak.json", "r") as read_file:
                data = json.load(read_file)

            for value in data.values():
                if value['delta'] is not None:
                    print(f"action={value['action']}, delta={value['delta']}, grace={value['delay']}")
                    streak_button = StreakButton(id=(value['action']), text=(value['action'] + " " + "[" + str(value['score']) + "]"),
                                                 color=(0,0,0,1), size=(400, 50),
                                                 size_hint=(None, None))
                    self.root.screen_two.ids.streak_zone.add_widget(streak_button)

                        # turns key of highest streak and its value into tuple
                    try:
                        self.highest = max((int(value['score']), key) for key, value in data.items())
                        self.high_string = "Highest Streak: \"%s\", with a streak of %s" % (self.highest[1], self.highest[0])
                        self.root.screen_two.ids.high_label.add_widget(Label(text=self.high_string,
                                                                        size_hint=(None,None), font_size=16))
                    except ValueError as error:
                        popup_2.open()
                        self.root.current = 'one'

        except (json.decoder.JSONDecodeError, FileNotFoundError) as error:
            popup_2.open()
            self.root.current = 'one'


    # update text that says the highest streak and its score
    def update_high(self, dt):
        for child in reversed(self.root.screen_two.ids.high_label.children):
            if child.text != self.high_string:
                self.root.screen_two.ids.high_label.remove_widget(child)
            elif child.text == self.high_string:
                pass


    # add 1 to score and store in json file
    def add_score(self, obj):
        name = obj.id

        with open("streak.json", "r") as file:
            read = json.load(file)

        for key in read.keys():
            if key == name:
                with open("streak.json", "r+") as f:
                    data = json.load(f)
                    data[key]['score']+=1

                    grace_sec = data.get(key, {}).get('grace_sec')
                    new_delay = time.time() + grace_sec
                    data[key]['delay'] = new_delay

                    seconds = data.get(key, {}).get('seconds')
                    new_delta = time.time() + seconds
                    data[key]['delta'] = new_delta

                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

    # change score to 0 and stores in json file
    def score_gone(self, dt):
        for child in self.root.screen_two.ids.streak_zone.children:
            name = child.id
            color = child.background_color

            if color == [1, 0, 0, .95]: # red
                with open("streak.json", "r") as file:
                    read = json.load(file)

                if read[name]['score'] != 0: #stops slow down from Clock
                    with open("streak.json", "r+") as f: # fix score not reseting to 0
                            data = json.load(f)
                            data[name]['score'] = 0
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()

                elif read[name]['score'] == 0: #stops slow down from Clock
                        pass


    # displays the streak that was clicked on in screen two
    def display_streak(self, obj):
        self.third_screen()

        name = obj.id
        bottle = self.root.get_screen('three')
        can = self.root.get_screen('two')

        with open("streak.json", "r") as file:
            read = json.load(file)

        if read[name]['score'] == 0:
            bottle.ids.selected_streak.add_widget(Label(id=name, text=(name + " " + "[" + str(read[name]['score']) + "]"),
                                                    size_hint=(None,None), font_size=18))
        else:
            bottle.ids.selected_streak.add_widget(Label(id=name, text=(name + " " + "[" + str(int(read[name]['score'] + 1)) + "]"),
                                                size_hint=(None,None), font_size=18))
        bottle.ids.del_space.add_widget(Button(id=name, text="Delete", size=(60,25), size_hint=(None,None),
                                    font_size=18, on_press=self.del_button))

    def draw_streak(self, obj):
        name = obj.id

        with open("streak.json", "r") as file:
            read = json.load(file)

        for key in read.keys():
            if key == name:
                with open("streak.json", "r+") as f:
                    data = json.load(f)

                get_score = data.get(key, {}).get('score')

        root = App.get_running_app().root
        can = root.get_screen('three')
        new_pos = can.pos
        new_pos[1] = root.height - 120 # below label

        for x in range(-1, get_score): # had to use -1 to get correct amount of shapes
            if get_score <= 70:
                with can.ids.my_box.canvas:
                    Color(0, 1, 0, .75, mode='rgba')
                    rect = Ellipse(pos=new_pos, size=(40,40))

                new_pos[0] += rect.size[0] * 2 # x coordinate
                if new_pos[0] >= (root.width - rect.size[0]):
                    new_pos[0] = 0
                    new_pos[1] -= rect.size[0] * 2 # y coordinate

            # following code makes rectangles smaller to fit the screen
            elif 70 < get_score < 260:
                with can.ids.my_box.canvas:
                    Color(0, 1, 0, .75, mode='rgba')
                    rect = Ellipse(pos=new_pos, size=(20,20))

                new_pos[0] += rect.size[0] * 2 # x coordinate
                if new_pos[0] >= (root.width - rect.size[0]):
                    new_pos[0] = 0
                    new_pos[1] -= rect.size[0] * 2 # y coordinate

            elif 260 > get_score > 70:
                with can.ids.my_box.canvas:
                    Color(0, 1, 0, .75, mode='rgba')
                    rect = Ellipse(pos=new_pos, size=(10,10))

                new_pos[0] += rect.size[0] * 2 # x coordinate
                if new_pos[0] >= (root.width - rect.size[0]):
                    new_pos[0] = 0
                    new_pos[1] -= rect.size[0] * 2 # y coordinate

            elif get_score >= 1000:
                with can.ids.my_box.canvas:
                    Color(0, 1, 0, .75, mode='rgba')
                    rect = Ellipse(pos=new_pos, size=(5,5))

                new_pos[0] += rect.size[0] * 2 # x coordinate
                if new_pos[0] >= (root.width - rect.size[0]):
                    new_pos[0] = 0
                    new_pos[1] -= rect.size[0] * 2 # y coordinate


    # deletes streaks
    def del_button(self, object):
        self.store = JsonStore("streak.json")
        name = object.id
        self.store.delete(name)
        self.change_screen()

    def update_label(self, dt):
        if self.root.current == "two":
            pass


    # creates the Streak object
    def create(self):
        self.store = JsonStore("streak.json")
        obj = self.root.get_screen('one')  # get info from ScreenOne
        self.streak = Streak(obj.ids.action_entry.text, obj.ids.delay_entry.text,
                             obj.ids.day_entry.text, obj.ids.hour_entry.text,
                             obj.ids.minute_entry.text)

        empty_error = "Make sure to fill out all boxes!"  # not in use yet

        popup = Popup(title="Not filled", content=Label(text=empty_error),
                      size_hint=(None, None), size=(300, 100))

        # error handling and calculating total seconds
        parsed = False
        try:
            total = ((int(self.streak.day) * 86400) + (int(self.streak.hour) * 3600) +
                     (int(self.streak.minute) * 60))  # convert into seconds

            self.current_time = time.time()
            self.count = self.current_time + total
            grace = (int(self.streak.delay) * 60) + self.count  # aka delay
            grace_sec = (int(self.streak.delay) * 60) + total

            parsed = True

            # delete later just used to test
            print("[seconds:", total, ']', "[action:", self.streak.action, ']',
                  "[grace:", grace, ']')

            # store streak attributes inside "streak.json"
            self.store.put(self.streak.action, action=self.streak.action,
                           delay=grace, seconds=total,
                           score=1, delta=self.count, grace_sec=grace_sec)

            self.change_screen(self)
        except ValueError as error:
            popup.open()


if __name__ == '__main__':
    MainApp().run()
