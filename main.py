from kivy.lang import Builder
from kivy.config import Config
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.togglebutton import ToggleButton

# kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from datetime import datetime, timedelta

Config.set("graphics", "width", "400")
# Config.set("graphics", "height", "750")

Builder.load_string('''

<SelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
<RV>:
    viewclass: 'SelectableLabel'
    SelectableRecycleBoxLayout:
        default_size: None, dp(35)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: True
        touch_multiselect: True

''')


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    selected_result = []
    selected_index = []
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''

        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''

        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''

        self.selected = is_selected
        if is_selected:
            self.selected_index.append(index)
            # self.selected_result.append(rv.data[index]['text'])
            # print(f"selected: {self.selected_index}")

        else:
            if index in self.selected_index:
                self.selected_index.remove(index)
                # print(f"updated: {self.selected_index}")
            pass


class BackgroundLayout(BoxLayout):
    pass


class CalButton(Button):
    pass


class MyLabel(Label):
    pass


class TimeCalculatorApp(App):
    RV_layout = RV()
    time_diffs = []
    time_diffs_list = []
    selected_time_diffs = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create the sliders for the start and end time
        self.start_time_slider = Slider(min=0, max=1439, step=0.1, value=0, size_hint=(1, None), height=40)
        self.end_time_slider = Slider(min=0, max=1439, step=0.1, value=0, size_hint=(1, None), height=40)

        # Create labels to display the start and end time
        self.end_time_label = MyLabel(text='End time: 00:00', size_hint=(1, None), height=60, pos_hint={"y":0})
        self.start_time_label = MyLabel(text='Start time: 00:00', size_hint=(1, None), height=60, pos_hint={"y":0})

        # Create a label to display the result
        self.result_label = MyLabel(text='', size_hint=(1, None), height=40, bold=True, color="red", font_size=dp(19))

    def build(self):
        # Create the main layout for the app
        layout = BackgroundLayout(orientation='vertical', spacing=10, padding=10)
        input_layout = BoxLayout(spacing=10, padding=10)
        slider_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        slider_start_layout = BoxLayout(pos_hint={"center_x":.5}, size_hint=(None, 1), width=dp(150))
        slider_end_layout = BoxLayout(pos_hint={"center_x":.5}, size_hint=(None, 1), width=dp(150))
        selection_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=40)

        # Create a toggle button to switch between timing mode
        self.timing_mode_btn = ToggleButton(text="24Hrs\nmode", size_hint=(.3, .9))
        self.timing_mode_btn.bind(on_press=self.toggle_timing_mode)

        self.am_pm_start_btn = ToggleButton(text="AM", size_hint=(None, None), opacity=0, width=dp(40), height=dp(25), pos_hint={"y":.2})
        self.am_pm_start_btn.bind(on_press=self.am_pm_switch)

        self.am_pm_end_btn = ToggleButton(text="AM", size_hint=(None, None), opacity=0, width=dp(40), height=dp(25),
                                          pos_hint={"y":.2})
        self.am_pm_end_btn.bind(on_press=self.am_pm_switch)

        # Add widget to input_layout
        input_layout.add_widget(self.timing_mode_btn)
        input_layout.add_widget(slider_layout)

        # Create a button to calculate the time difference
        calculate_button = CalButton(text='Calculate', size_hint=(1, None), height=40)
        calculate_button.bind(
            on_press=lambda x: self.calculate_time_difference(self.start_time_slider.value, self.end_time_slider.value,
                                                              self.result_label))

        # Add the widgets to the slider_layout
        slider_layout.add_widget(self.start_time_slider)
        slider_start_layout.add_widget(self.start_time_label)
        slider_start_layout.add_widget(self.am_pm_start_btn)
        slider_layout.add_widget(slider_start_layout)
        slider_layout.add_widget(self.end_time_slider)
        slider_end_layout.add_widget(self.end_time_label)
        slider_end_layout.add_widget(self.am_pm_end_btn)
        slider_layout.add_widget(slider_end_layout)
        layout.add_widget(input_layout)
        layout.add_widget(calculate_button)
        layout.add_widget(self.result_label)

        # Create a box layout to hold the time difference labels and the selection buttons
        layout.add_widget(self.RV_layout)

        # Create a button to add the selected time difference labels
        add_button = Button(text='Add', size_hint=(0.5, None), height=40)
        add_button.bind(
            on_press=lambda instance: self.add_time_differences(SelectableLabel.selected_index, self.result_label))

        # Create a button to Reset all
        reset_button = Button(text='Reset', size_hint=(0.5, None), height=40)
        reset_button.bind(on_press=lambda instance: self.reset_func())

        # Add the selection buttons to the layout
        selection_layout.add_widget(add_button)
        selection_layout.add_widget(reset_button)
        layout.add_widget(selection_layout)

        # Update the start and end time labels when the sliders are moved
        self.start_time_slider.bind(
            value=lambda x, y: self.update_time_label(self.start_time_slider, self.start_time_label))
        self.end_time_slider.bind(value=lambda x, y: self.update_time_label(self.end_time_slider, self.end_time_label))

        return layout

    def update_time_label(self, slider, label):
        # Convert the slider value to a datetime object
        time_obj = datetime.strptime(str(timedelta(minutes=slider.value)), '%H:%M:%S')

        # Format the time as hh:mm
        time_str = time_obj.strftime('%H:%M')

        # Update the label
        label.text = f'{label.text.split(":")[0]}: {time_str}'

    def toggle_timing_mode(self, instance):
        if instance.state == 'down':
            instance.text = "12Hrs\nmode"
            self.mode_12hrs()

        else:
            instance.text = "24Hrs\nmode"
            self.mode_24hrs()

    def convert_time(self, start_time, end_time):
        # start_time = "2:30 PM"
        # end_time = "10:45 AM"
        if self.timing_mode_btn.state == "down":
            time1_obj = datetime.strptime(f'{int(start_time) // 60:02d}:{int(start_time) % 60:02d} {self.am_pm_start_btn.text}',
                "%I:%M %p")
            time2_obj = datetime.strptime(f'{int(end_time) // 60:02d}:{int(end_time) % 60:02d} {self.am_pm_end_btn.text}',
                "%I:%M %p")
        else:
            time1_obj = datetime.strptime(f'{int(start_time) // 60:02d}:{int(start_time) % 60:02d}',
                                              '%H:%M')
            time2_obj = datetime.strptime(f'{int(end_time) // 60:02d}:{int(end_time) % 60:02d}',
                                            '%H:%M')

        return time1_obj, time2_obj

    def am_pm_switch(self, widget):
        if widget.state == "down":
            widget.text = "PM"
            hour = 12
        else:
            widget.text = "AM"
            hour = 0
        return hour

    def calculate_time_difference(self, start_time_minutes, end_time_minutes, result_label):
        SelectableLabel.selected_index = []
        start_time_dt, end_time_dt = self.convert_time(start_time_minutes, end_time_minutes)
        # print(start_time_dt, end_time_dt)

        if start_time_minutes == end_time_minutes:
            time_diff_str = '24:00'
        elif start_time_minutes < end_time_minutes:
            time_diff_obj = end_time_dt - start_time_dt
            time_diff_str = f'{time_diff_obj.seconds // 3600:02d}:{(time_diff_obj.seconds // 60) % 60:02d}'
        else:
            if end_time_dt < start_time_dt:
                end_time_dt += timedelta(days=1)
            time_diff_obj = end_time_dt - start_time_dt
            time_diff_str = f'{time_diff_obj.seconds // 3600:02d}:{(time_diff_obj.seconds // 60) % 60:02d}'

        time_diff_seconds = self.timestr_to_timeint(time_diff_str)
        self.time_diffs.append(int(time_diff_seconds))

        result_label.text = f'Time difference: {time_diff_str}hrs'
        self.time_diffs_list.append(time_diff_str)
        self.RV_layout.data = [{'text': str(x)} for x in self.time_diffs_list]
        # print(self.time_diffs)

    def timestr_to_timeint(self, str_value):
        hours, minutes = str_value.split(':')
        hours_int = int(hours)
        minutes_int = int(minutes)
        total_minutes = hours_int * 60 + minutes_int
        total_seconds = total_minutes * 60
        return total_seconds

    def add_time_differences(self, selected_index, result_label):
        self.selected_time_diffs = []
        for index in selected_index:
            time_diff = self.time_diffs[index]
            self.selected_time_diffs.append(time_diff)

        # print(self.selected_time_diffs)
        # Calculate the total time difference
        total_time_diff = sum(self.selected_time_diffs)
        # print(total_time_diff)

        # Convert total_time_diff to hours and minutes
        total_hours, total_seconds = divmod(total_time_diff, 3600)
        total_minutes, _ = divmod(total_seconds, 60)

        # Create a formatted string for the total time difference
        total_time_diff_str = f'{total_hours}hrs {total_minutes}min'

        # Update the result label
        result_label.text = f'Total time: {total_time_diff_str}'

    def mode_12hrs(self):
        self.am_pm_start_btn.opacity = 1
        self.am_pm_end_btn.opacity = 1
        self.start_time_slider.min = 60
        self.end_time_slider.min = 60
        self.start_time_slider.max = 779
        self.end_time_slider.max = 779
        self.start_time_slider.value = 60
        self.end_time_slider.value = 60

    def mode_24hrs(self):
        self.timing_mode_btn.state = "normal"
        self.timing_mode_btn.text = "24Hrs\nmode"
        self.am_pm_start_btn.opacity = 0
        self.am_pm_end_btn.opacity = 0

        self.start_time_slider.min = 0
        self.end_time_slider.min = 0
        self.start_time_slider.max = 1439
        self.end_time_slider.max = 1439
        self.start_time_slider.value = 0
        self.end_time_slider.value = 0

    def reset_func(self):
        self.mode_24hrs()
        self.start_time_label.text = 'Start time: 00:00'
        self.end_time_label.text = 'End time: 00:00'
        self.result_label.text = ""
        SelectableLabel.index = None
        SelectableLabel.selected_index = []
        self.RV_layout.data = ""
        self.time_diffs = []
        self.time_diffs_list = []
        self.selected_time_diffs = []


TimeCalculatorApp().run()



