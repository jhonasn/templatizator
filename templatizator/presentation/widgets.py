''' A little modified tk_ToolTip_class101.py by vegaseat that
gives a tkinter widget a tooltip as the mouse is above the widget
tested with python37 by jhonasn 15sep2018
'''
import tkinter as tk


class Tooltip:
    '''
    Create a tooltip for a given widget.
    Inform col to add tooltip to a treeview column
    '''
    def __init__(self, widget, text='widget info', col=None, before=None):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.col = col
        self.before = before

        if col:
            self.widget.bind('<Motion>', self.enter)
        else:
            self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        '''Shows the tooltip when mouse enter'''
        point = {'x': 0, 'y': 0}
        point['x'] += self.widget.winfo_rootx() + 25
        point['y'] += self.widget.winfo_rooty() + 20
        if self.col:
            self.close(event)
            col = self.widget.identify_column(event.x)
            iid = self.widget.identify('item', event.x, event.y)
            if (col != self.col and self.col != '#') or not iid:
                # do not show tooltip
                return
            if self.before:
                show = self.before(col, iid, self)
                if not show:
                    return
            point['x'] += event.x
            point['x'] -= 15
            point['y'] += event.y
            point['y'] -= 10
        # creates a toplevel window
        self.tooltip_window = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry("+%d+%d" % (point['x'], point['y']))
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background='#f7f7da', relief='solid', borderwidth=1,
                         font=("times", "8", "normal"))
        label.pack(ipadx=1)

    # pylint: disable=unused-argument
    def close(self, event=None):
        '''Closes tooltip when mouse leaves'''
        if self.tooltip_window:
            self.tooltip_window.destroy()
