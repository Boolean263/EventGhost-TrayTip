# EventGhost-TrayTip

This program is not very useful on its own. It's a plugin for
[EventGhost](http://www.eventghost.net/).
EventGhost is an automation tool for MS Windows
which listens for events -- whether user-triggered (like the press of a hotkey)
or system events (such as the screensaver activating) -- and runs actions
you specify. (It's like [Tasker](http://tasker.dinglisch.net/) for Android, or
[Cuttlefish](https://launchpad.net/cuttlefish) for Ubuntu.)

## Description

TrayTip is an action plugin (mostly) for EventGhost. It lets you add an
action to your macros that shows a pop-up message in the Windows notification
area. This message is mostly useful for informing the user of something,
but you can also click it to generate an event.

## Usage

Adding a TrayTip action to your EventGhost macro is no different from
most other actions. The configuration dialog prompts you for several items:

* Icon: the icon you wish to appear on the pop-up. Supports built-in values
  for no icon, info, warning, error, and the EventGhost icon, as well as
  letting you choose a custom icon from a EXE, DLL, or ICO file.
* Title: this is typically shown in a large, bold font.
* Message: some more detail about what you're telling the user.
* Payload: an optional string payload to include in generated events
  (see below).
* Sound: whether to play the default notification sound or not.

The title, message, and payload are parsed for python code wrapped in {curly
braces}.  If you want to include an actual curly brace, you need to double it
up, as in "{{".

You can also call
`eg.plugins.TrayTip.ShowTip(title, msg, payload, iconOpt, sound)`
directly from a python script action if you wish. The payload is still
optional, and doesn't have to be a string (but is only parsed for python
if it is a string). If iconOpt and sound aren't specified, they respectively
default to the EventGhost icon and sound enabled.

This plugin can generate four different types of event for each notification
shown. In all cases, the event will have the payload you specified, which
can be accesseed from an action by using `eg.event.payload`.

* `TrayTip.Show`: a new notification is being shown to the user.
* `TrayTip.Hide`: the notification is being hidden.
* `TrayTip.TimedOut`: the notification went away without being clicked.
* `TrayTip.Clicked`: the user clicked the notification. This is probably
  the most useful one to use in your other actions, since it's the only one
  that indicates actual user activity.

There is currently no way to distinguish what notification was clicked on
by reading the event object, apart from using a known value that you
put in the payload. If you think of other useful information that could
be added to the payload, let me know.

## Downloads and Support

Official releases of this plugin are being made available at
[this thread on the EventGhost forums](http://www.eventghost.net/forum/viewtopic.php?f=9&t=9794).
You can also provide feedback and request support there.

I also accept issues and pull requests from the official GitHub repo for
this project,
[Boolean263/EventGhost-TrayTip](https://github.com/Boolean263/EventGhost-TrayTip).

## Future Improvements

It would be really useful to create notifications that persist in the
Windows 10 Action Center. I haven't found information on how to do that yet.

I'm told you can add buttons to notification pop-ups. That'd be cool too.

## Authors

* Boolean263, aka David Perry
* Kevin Schlosser
* topic2k

## Changelog

### v0.1.2 - 2017-09-03

* Expand path variables (like `%SystemRoot%`) in icon paths (thanks topic2k)

### v0.1.1 - 2017-09-03

* Bugfix: load .ICO files properly
* Hide configuration dialog while the icon chooser is visible, to prevent
  users from closing the configuration dialog with the icon chooser still
  visible (thus causing an EventGhost crash)

### v0.1.0 - 2017-09-02

* Improvements from kgschlosser
* Generate events for all actions (though Clicked is still the most useful)
* New API (`ShowTip()` instead of `showTip()`)
* Add icon selection (none, info, warning, error, EventGhost, custom)
  and icon chooser for custom icons
* Optionally disable notification sound
* Clean up resource leaks
* Some work to help the plugin deactivate cleanly if it's deactivated
  while a notification is still visible

### v0.0.1 - 2017-08-21

* Initial release
