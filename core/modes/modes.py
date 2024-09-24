from talon import Context, Module, actions, app, speech_system

mod = Module()
ctx_sleep = Context()
ctx_awake = Context()

modes = {
    "presentation": "a more strict form of sleep where only a more strict wake up command works",
}

for key, value in modes.items():
    mod.mode(key, value)

ctx_sleep.matches = r"""
mode: sleep
"""

ctx_awake.matches = r"""
not mode: sleep
"""


@ctx_sleep.action_class("speech")
class ActionsSleepMode:
    def disable():
        actions.app.notify("Talon is already asleep")


@ctx_awake.action_class("speech")
class ActionsAwakeMode:
    def enable():
        actions.app.notify("Talon is already awake")


class ModeState:
    def __init__(self):
        self.previous_mode = None
        self.speech_enabled = None

mode_state = ModeState()

@mod.action_class
class Actions:
    def command_mode():
        """Enable command mode"""
        actions.mode.disable("sleep")
        actions.mode.disable("dictation")
        actions.mode.enable("command")

    def dictation_mode():
        """Enable dictation mode"""
        actions.mode.disable("sleep")
        actions.mode.disable("command")
        actions.mode.enable("dictation")
        actions.user.code_clear_language_mode()
        actions.user.gdb_disable()

    def talon_mode():
        """For windows and Mac with Dragon, enables Talon commands and Dragon's command mode."""
        actions.speech.enable()

        engine = speech_system.engine.name
        # app.notify(engine)
        if "dragon" in engine:
            if app.platform == "mac":
                actions.user.dragon_engine_sleep()
            elif app.platform == "windows":
                actions.user.dragon_engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.dragon_engine_command_mode()

    def dragon_mode():
        """For windows and Mac with Dragon, disables Talon commands and exits Dragon's command mode"""
        engine = speech_system.engine.name
        # app.notify(engine)

        if "dragon" in engine:
            # app.notify("dragon mode")
            actions.speech.disable()
            if app.platform == "mac":
                actions.user.dragon_engine_wake()
            elif app.platform == "windows":
                actions.user.dragon_engine_wake()
                # note: this may not do anything for all versions of Dragon. Requires Pro.
                actions.user.dragon_engine_normal_mode()

    def whisper_mode():
        """Enter whisper mode"""
        print("Entering whisper mode")
        # mode_state.previous_mode = actions.mode.current()
        mode_state.speech_enabled = actions.speech.enabled()
        actions.mode.disable("command")
        actions.mode.enable("user.whisper")

    def stop_whisper_mode():
        """Exit whisper mode and restore previous state"""
        print("Exiting whisper mode")
        actions.mode.disable("user.whisper")
        actions.mode.enable("command")
        # if mode_state.previous_mode:
        #     actions.mode.enable(mode_state.previous_mode)
        if mode_state.speech_enabled:
            actions.speech.enable()
            print("Speech enabled")
        else:
            actions.speech.disable()
            actions.mode.disable("command")
            print("Speech DISabled")
