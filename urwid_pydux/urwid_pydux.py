from urwid import WidgetPlaceholder
from pydux.extend import extend


def subscribe_urwid_redraw(store, loop):
    last_state = [None]  # r/w closure
    get_state = store['get_state']

    def maybe_redraw():
        state = get_state()
        if not last_state[0] is state:
            last_state[0] = state
            loop.draw_screen()

    return store['subscribe'](maybe_redraw)


class Component(WidgetPlaceholder):
    def __init__(self, store):
        self.store = store
        self.props = self.map_state_to_props(store['get_state']())
        self.unsubscribe = store['subscribe'](self.on_state_change)

        self.component_will_mount(store)

        final_props = self.combine_props()
        super(Component, self).__init__(
            self.render_component(self.store, final_props)
        )

    def __del__(self):
        if self.unsubscribe and hasattr(self.unsubscribe, '__call__'):
            self.unsubscribe()

    def map_dispatch_to_props(self, dispatch):
        return {}

    def map_state_to_props(self, state):
        return {}

    def component_will_mount(self, store):
        pass

    def combine_props(self):
        dispatch = self.store['dispatch']
        return extend(self.props, self.map_dispatch_to_props(dispatch))

    def on_state_change(self):
        state = self.store['get_state']()
        new_props = self.map_state_to_props(state)
        if new_props != self.props:
            self.props = new_props
            final_props = self.combine_props()
            new_widget = self.render_component(self.store, final_props)
            self.original_widget = new_widget
