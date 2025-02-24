# -*- coding: utf-8 -*-

# Standard library imports
import sys

from qtawesome import icon, IconWidget, Spin, Pulse, font, set_global_defaults
# Third party imports
from qtpy import QtCore, QtWidgets


class AwesomeExample(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # Label for supported fonts
        supported_fonts_label = QtWidgets.QLabel('Supported fonts (prefix)')
        supported_fonts_label.setAlignment(QtCore.Qt.AlignCenter)

        # Get FontAwesome 5.x icons by name in various styles by name
        fa5_icon = icon('fa5.file-alt')
        fa5_button = QtWidgets.QPushButton(fa5_icon, 'Font Awesome regular (fa5)')

        fa5s_icon = icon('fa5s.flag')
        fa5s_button = QtWidgets.QPushButton(fa5s_icon, 'Font Awesome solid (fa5s)')

        fa5b_icon = icon('fa5b.github')
        fa5b_button = QtWidgets.QPushButton(fa5b_icon, 'Font Awesome brands (fa5b)')

        # Get Elusive icons by name
        asl_icon = icon('ei.asl')
        elusive_button = QtWidgets.QPushButton(asl_icon, 'Elusive Icons (ei)')

        # Get Material Design icons by name
        apn_icon = icon('mdi6.access-point-network')
        mdi6_button = QtWidgets.QPushButton(apn_icon, 'Material Design (mdi, mdi6)')

        # Get Phosphor by name
        mic_icon = icon('ph.microphone-fill')
        ph_button = QtWidgets.QPushButton(mic_icon, 'Phosphor Icons (ph)')

        # Get Remix Icon by name
        truck_icon = icon('ri.truck-fill')
        ri_button = QtWidgets.QPushButton(truck_icon, 'Remix Icons (ri)')

        # Get Microsoft's Codicons by name
        squirrel_icon = icon('msc.squirrel')
        msc_button = QtWidgets.QPushButton(squirrel_icon, 'Codicons (msc)')

        # Label for style options and animations
        styles_label = QtWidgets.QLabel('Styles')
        styles_label.setAlignment(QtCore.Qt.AlignCenter)

        # Rotated
        rot_icon = icon('mdi.access-point-network', rotated=45)
        rot_button = QtWidgets.QPushButton(rot_icon, 'Rotated Icons')

        # Horizontal flip
        hflip_icon = icon('mdi.account-alert', hflip=True)
        hflip_button = QtWidgets.QPushButton(hflip_icon, 'Horizontally Flipped Icons')

        # Vertical flip
        vflip_icon = icon('mdi.account-alert', vflip=True)
        vflip_button = QtWidgets.QPushButton(vflip_icon, 'Vertically Flipped Icons')

        # Styling
        styling_icon = icon('fa5s.music',
                                active='fa5s.balance-scale',
                                color='blue',
                                color_active='orange')
        music_button = QtWidgets.QPushButton(styling_icon, 'Changing colors')

        # Setting an alpha of 165 to the color of this icon. Alpha must be a number
        # between 0 and 255.
        icon_with_alpha = icon('mdi.heart', color=('red', 120))
        heart_button = QtWidgets.QPushButton(icon_with_alpha, 'Setting alpha')

        # Toggle
        toggle_icon = icon('fa5s.home', selected='fa5s.balance-scale',
                               color_off='black',
                               color_off_active='blue',
                               color_on='orange',
                               color_on_active='yellow')
        toggle_button = QtWidgets.QPushButton(toggle_icon, 'Toggle')
        toggle_button.setCheckable(True)

        iconwidget = IconWidget()
        spin_icon = icon('mdi.loading', color='red',
                             animation=Spin(iconwidget))
        iconwidget.setIcon(spin_icon)
        iconwidget.setIconSize(QtCore.QSize(32, 32))
        iconwidgetholder = QtWidgets.QWidget()
        lo = QtWidgets.QHBoxLayout()
        lo.addWidget(iconwidget)
        lo.addWidget(QtWidgets.QLabel('IconWidget'))
        iconwidgetholder.setLayout(lo)
        iconwidget2 = IconWidget('mdi.web', color='blue', size=QtCore.QSize(16, 16))

        # Icon drawn with the `image` option
        drawn_image_icon = icon('ri.truck-fill',
                                    options=[{'draw': 'image'}])
        drawn_image_button = QtWidgets.QPushButton(drawn_image_icon,
                                                   'Icon drawn as an image')

        # Stack icons
        camera_ban = icon('fa5s.camera', 'fa5s.ban',
                              options=[{'scale_factor': 0.5,
                                        'active': 'fa5s.balance-scale'},
                                       {'color': 'red', 'opacity': 0.7}])
        stack_button = QtWidgets.QPushButton(camera_ban, 'Stack')
        stack_button.setIconSize(QtCore.QSize(32, 32))

        # Stack and offset icons
        saveall = icon('fa5.save', 'fa5.save',
                           options=[{'scale_factor': 0.8,
                                     'offset': (0.2, 0.2),
                                     'color': 'gray'},
                                    {'scale_factor': 0.8}])
        saveall_button = QtWidgets.QPushButton(saveall, 'Stack, offset')

        # Spin icons
        spin_button = QtWidgets.QPushButton(' Spinning icon')
        animation1 = Spin(spin_button)
        spin_icon = icon('fa5s.spinner', color='red', animation=animation1)
        spin_button.setIcon(spin_icon)

        timer1 = QtCore.QTimer()
        timer1.singleShot(3000, animation1.stop)

        # Pulse icons
        pulse_button = QtWidgets.QPushButton(' Pulsing icon')
        animation2 = Pulse(pulse_button, autostart=False)
        pulse_icon = icon('fa5s.spinner', color='green',
                              animation=animation2)
        pulse_button.setIcon(pulse_icon)

        timer2 = QtCore.QTimer()
        timer2.singleShot(1500, animation2.start)
        timer3 = QtCore.QTimer()
        timer3.singleShot(6000, animation2.stop)

        # Stacked spin icons
        stack_spin_button = QtWidgets.QPushButton('Stack spin')
        options = [{'scale_factor': 0.4,
                    'animation': Spin(stack_spin_button)},
                   {'color': 'blue'}]
        stack_spin_icon = icon('ei.asl', 'fa5.square',
                                   options=options)
        stack_spin_button.setIcon(stack_spin_icon)
        stack_spin_button.setIconSize(QtCore.QSize(32, 32))

        # Render a label with this font
        label = QtWidgets.QLabel(chr(0xf19c) + ' ' + 'Label')
        label.setFont(font('fa', 16))

        # Layout
        grid = QtWidgets.QGridLayout()
        fonts_widgets = [
            supported_fonts_label,
            fa5_button,
            fa5s_button,
            fa5b_button,
            elusive_button,
            mdi6_button,
            ph_button,
            ri_button,
            msc_button,
        ]
        styled_widgets = [
            styles_label,
            music_button,
            heart_button,
            rot_button,
            hflip_button,
            vflip_button,
            toggle_button,
            drawn_image_button
        ]
        animated_widgets = [
            spin_button,
            pulse_button,
            stack_button,
            saveall_button,
            stack_spin_button,
        ]
        other_widgets = [
            label,
            iconwidgetholder,
            iconwidget2
        ]

        for idx, w in enumerate(fonts_widgets):
            grid.addWidget(w, idx, 0)

        for idx, w in enumerate(styled_widgets):
            grid.addWidget(w, idx, 1)

        for idx, w in enumerate(animated_widgets):
            grid.addWidget(w, idx + len(styled_widgets), 1)

        for idx, w in enumerate(other_widgets):
            grid.addWidget(w, idx + len(styled_widgets) + len(animated_widgets), 1)

        title = 'Awesome'
        args = ' '.join(sys.argv[1:]).strip()
        if args:
            title += ' (' + args + ')'

        self.setLayout(grid)
        self.setWindowTitle(title)
        self.setMinimumWidth(520)
        self.show()


def main():

    global_defaults = {}
    for arg in sys.argv[1:]:
        try:
            key, val = arg.split('=', maxsplit=1)
            global_defaults[key] = val
        except:
            pass
    if global_defaults:
        set_global_defaults(**global_defaults)

    app = QtWidgets.QApplication(sys.argv)

    # Enable High DPI display with PyQt5
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

    # Timer needed to close the example application
    # when testing
    QtCore.QTimer.singleShot(10000, app.exit)
    _ = AwesomeExample()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()