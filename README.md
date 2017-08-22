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
most other actions. The configuration dialog prompts you for three items:

* Title: this is typically shown in a large, bold font.
* Message: some more detail about what you're telling the user.
* Payload: an optional string payload to include in the generated event
  (see below) if the user clicks on the notification.

All three items are parsed for python code wrapped in {curly braces}.
If you want to include an actual curly brace, you need to double it up,
as in "{{".

You can also call `eg.plugins.TrayTip.showTip(title, msg, payload)`
directly from a python script action if you wish. The payload is still
optional, and doesn't have to be a string.

If the user clicks on the notification that gets popped up by this plugin,
the plugin will generate a `TrayTip.Clicked` event with the specified
payload. You can access this payload from an action using `eg.event.payload`.
If the notification is left to vanish on its own, no event is generated.

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

It would be useful to make configurable the icon which shows in the
notification. Currently it's hard-coded to use the EventGhost icon.
This shouldn't be hard, I just haven't gotten that far yet.

It would be really useful to create notifications that persist in the
Windows 10 Action Center. I haven't found information on how to do that yet.

## Authors

Boolean263, aka David Perry, and Kevin Schlosser

## Changelog

### v0.0.1 - 2017-08-21

* Initial release
