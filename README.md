Cappuccino support for ST3
==========================

[![Build Status](https://travis-ci.org/aparajita/Cappuccino-Sublime.svg?branch=master)](https://travis-ci.org/aparajita/Cappuccino-Sublime)

This language bundle for [Sublime Text 3](http://sublimetext.com/3) provides extensive support for [Cappuccino](http://www.cappuccino-project.org), including:

* Full syntax highlighting for Objective-J source (.j files)
* Symbol lists which include classes, protocols, methods, macro functions, and Javascript functions
* Smart balancing of square brackets in message sends
* Smart alignment of ':' parameter separators
* Many snippets to reduce typing

**NOTE:** This version is for Sublime Text 3, the Sublime Text 2 version is [here](https://github.com/aparajita/Cappuccino-Sublime/tree/st2).

## Installation
Please use [Package Control](https://sublime.wbond.net/installation) to install this bundle. This will ensure that the bundle will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette](http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html) and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `cappuccino`. Among the entries you should see `Cappuccino`. If that entry is not highlighted, use the keyboard or mouse to select it.

Once the bundle is installed, to take advantage of the smart bracket balancing, you will need to install ruby. On Mac OS X, ruby is already installed. On Linux and Windows, you can follow the installation instructions [here](https://www.ruby-lang.org/en/installation/). To specify the path to particular ruby, use the `ruby_path` setting, as described [below](#ruby_path).

## Smart bracket balancing
If you have ruby installed, whenever you type `]` the current line of code is parsed and an attempt is made to determine if you are closing an Objective-J message send, and if so inserts a `[` in the appropriate place and adds a space before the `]`. For example, if you have typed

```objj
var dict = [CPDictionary alloc]
```

then type `]`, the parser will figure out that you are making a nested message send, and will change the line to:

```objj
var dict = [[CPDictionary alloc] ]
```

and place the cursor just before the second `]`. The parser will also handle a case like this:

```objj
var b = [self bar];
```

Let's assume you realize that `self` needs to be `[self foo]`, you can place the cursor to the right of `self` and type `]`. The parser will change the line to

```objj
var b = [[self ] bar];
```

with the cursor just before the first `]`. Very handy!

## Smart ':' alignment
Here's a common scenario: you want to send the message `doSomething:withOneThing:andAnother:andOneMoreThing:`. You know that it will be easier to read if you split it up into multiple lines. But the Cappuccino/Cocoa coding standard is to align colons on message sends split over multiple lines. You can do this manually, but it’s a pain.

This bundle automatically aligns colons as you type. For example, you start typing:

```objj
    [self doSomething:something]
```

Then you press Return and type `withOneThing`. At this point, assuming you have auto indentation on, you will have:

```objj
    [self doSomething:something
    withOneThing]
```

Normally, you would have to back up and insert space in front of `withOneThing` to line up the end of that word with the end of `doSomething` on the line above. But with this bundle, when you type `:`, the line is aligned for you:

```objj
    [self doSomething:something
         withOneThing:]
```

The cursor is after the `:`, so you can keep typing. This also works when typing method declarations, and actually works whenever you type `:` on a line within a method declaration or message send if there are no preceding square brackets on the line.

If you have an existing method declaration or message send that you want to split into multiple lines, you no longer have to manually line up the colons. If you place the cursor anywhere in within a method parameter and press Enter/Return, a colon to the right is aligned with the first colon in the method name.

For example, given this method declaration:

```objj
- (void)doSomething:(CPString)something withOneThing:(CPObject)oneThing andAnother:(CPArray)another
```

if you place the cursor before `withOneThing` (or anywhere in the whitespace before it) and press Enter/Return, the line is wrapped to align the colons:

```objj
- (void)doSomething:(CPString)something
       withOneThing:(CPObject)oneThing andAnother:(CPArray)another
```

Note that the anchor point for the align is the colon after the **first** method parameter on the line, so in the example above, if you had placed the cursor before `andAnother`, you would get this:

```objj
- (void)doSomething:(CPString)something withOneThing:(CPObject)oneThing
         andAnother:(CPArray)another
```

Wrapping of existing lines also works with message sends, so given this:

```objj
    [self doSomething:something withOneThing:one andAnother:another];
```

if you place the cursor before `withOneThing` (or within the whitespace before it) and press Enter/Return, you get:

```objj
    [self doSomething:something
         withOneThing:one andAnother:another];
```

Note that within message sends, alignment occurs with the closest containing message send, so for example if you are typing this, with the cursor just after `bar` on the second line:

```objj
    [self doSomething:something withOneThing:one andAnother:[self foo:woo
    bar]];
```

when you type `:` you will get this:

```objj
    [self doSomething:something withOneThing:one andAnother:[self foo:woo
                                                                  bar:]];
```

because the alignment is with the closest containing message send.

## Symbol lookup
On Mac OS X, this bundle provides documentation lookup for symbols using [Dash](http://kapeli.com/dash). The symbol that is looked up depends on the current selection (or the first selection if there are multiple selections):

* If the selection, expanded to word boundaries, begins with "CP", and is not within a method or protocol declaration, the word is looked up. This is ideal for looking up constants.

* If the selection is within a method, the containing method and its class or protocol is looked up.

* If the selection is not within a method, the containing class or protocol is looked up.

* If the selection is within Objective-J source, the selected text is looked up.

A "CP" name prefix is converted to "NS" for the lookup.

## Settings
Settings control the behavior of this bundle. The default settings with descriptions can be viewed by selecting the menu Preferences->Package Settings->Cappuccino->Settings - Default. You should never edit this file, it is there only for reference. A copy of the default settings is copied to the Sublime Text "User" directory when this language bundle is loaded. An existing user settings file is not overwritten.

### ruby_path
If you want to use a particular instance of ruby for smart bracket balancing, or if the bundle has trouble finding your system’s default ruby, you can set a path to a ruby executable in this setting. If using backslashes on Windows, be sure to double them. Note that `~` will be converted into the path to your home directory.

```
"ruby_path": "~/.rbenv/shims/ruby"
"ruby_path": "c:\\ruby\\ruby.exe"
```

## Snippets
This bundle provides a large variety of snippets to handle common Cappuccino coding tasks.

**Geometry**

| Trigger | Name |
| ------- | :-----|
| pt      | CGPointEqualToPoint |
| pt      | CGPointMake |
| pt      | CGPointMakeZero |
| rect    | CGRectMake |
| rect    | CGRectMakeZero |

**CPColor**

| Trigger | Name |
| ------- | :---- |
| color   | CPColor clear |
| color   | CPColor hex |
| color   | CPColor random |
| color   | CPColor rgb float |
| color   | CPColor rgb int |
| color   | CPColor white float |
| color   | CPColor white int |

**Debugging**

| Trigger | Name |
| ------- | :---- |
| db      | debugger |
| di      | dump inset to console |
| dp      | dump point to console |
| dr      | dump rect to console |
| ds      | dump size to console |
| log     | console.log |

**setAutoresizingMask**

| Trigger | Name |
| ------- | :---- |
| mbl     | setAutoresizingMask: bottom left |
| mbr     | setAutoresizingMask: bottom right |
| mc      | setAutoresizingMask: center |
| mf      | setAutoresizingMask: full resize |
| mhl     | setAutoresizingMask: resize height left |
| mhr     | setAutoresizingMask: resize height right |
| mtl     | setAutoresizingMask: top left |
| mtr     | setAutoresizingMask: top right |
| mwb     | setAutoresizingMask: resize width bottom |
| mwt     | setAutoresizingMask: resize width top |

**Miscellaneous**

| Trigger | Name |
| ------- | :---- |
| ac      | action method |
| acc     | @accessors |
| asv     | add subview |
| cat     | new category |
| cl      | new class |
| delr    | delegate responds to selector |
| gs      | getter/setter |
| imp     | import "…" |
| imp     | import &lt;…&gt; |
| init    | -init |
| init    | -initWithFrame |
| init    | -initWithFrame method |
| mark    | pragma mark - |
| res     | responds to selector |
| sel     | @selector |
| shadow  | add text shadow to CPControl |
| text    | new editable text field |
| text    | new label |

## Contributing
If you would like to contribute enhancements or fixes, please do the following:

1. Fork the plugin repository.
1. Hack on a separate topic branch created from the latest `master`.
1. Commit and push the topic branch.
1. Make a pull request.
1. Be patient.  ;-)

Please note that modications should follow these coding guidelines:

- Indent is 4 spaces.
- Code should pass flake8 linter.
- Vertical whitespace helps readability, don’t be afraid to use it.

Thank you for helping out!
