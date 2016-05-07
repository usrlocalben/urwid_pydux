from urwid import WidgetPlaceholder
from pydux.extend import extend


class Component(WidgetPlaceholder):
    """
    Component subclasses WidgetPlaceholder, since
    it is more-or-less equivalent to a <div>.

    This provides a React-ish API to use as a base
    for implementing connect().
    """
    prop_types = {}

    def __init__(self, **props):
        self.props = props
        self.ensure_props_are_valid(props)
        self.component_will_mount(props)
        super(Component, self).__init__(
            self.render_component(self.props)
        )

    def __del__(self):
        self.component_will_unmount()

    def component_will_mount(self, props):
        pass

    def component_will_unmount(self):
        pass

    def render_component(self, props):
        raise NotImplementedError()

    def ensure_props_are_valid(self, props):
        spec_keys = set(self.prop_types.keys())
        given_keys = set(props.keys())

        unknown = given_keys - spec_keys
        if unknown:
            msg = 'Component received unknown props: ' + str(unknown)
            raise Exception(msg)

        missing = spec_keys - given_keys
        if missing:
            msg = 'Component is missing props: ' + str(missing)
            raise Exception(msg)

        # TODO prop type checking
        # TODO is_required checking


class ConnectedComponent(Component):
    """
    Component that binds props to the pydux store.

    Based on react-redux's connect().
    """
    prop_types = {}

    def __init__(self, **props):
        """
        Note: All of parent's __init__ is replaced here.
        WidgetPlaceholder.__init__ is called directly.
        """
        try:
            self.store = props['store']
        except KeyError:
            raise Exception('store not found in props')

        self.prop_types = extend({'store': dict}, self.prop_types)
        self.ensure_props_are_valid(props)

        self.own_props = props
        self._cached_props = self.combine_props()
        self._unsubscribe = self.store['subscribe'](self.on_state_change)

        self.component_will_mount(self._cached_props)

        WidgetPlaceholder.__init__(self,
            self.render_component(self._cached_props)
        )

    def __del__(self):
        if self._unsubscribe and hasattr(self._unsubscribe, '__call__'):
            self._unsubscribe()
        super(ConnectedComponent, self).__del__()

    def map_dispatch_to_props(self, dispatch, own_props):
        return {}

    def map_state_to_props(self, state, own_props):
        return {}

    def combine_props(self):
        return extend(
            self.own_props,
            self.map_state_to_props(self.store['get_state'](), self.own_props),
            self.map_dispatch_to_props(self.store['dispatch'], self.own_props),
        )

    def on_state_change(self):
        new_props = self.combine_props()
        if new_props != self._cached_props:
            self._cached_props = new_props
            self.original_widget = self.render_component(new_props)


def subscribe_urwid_redraw(store, loop):
    """
    issue a redraw request to the urwid MainLoop
    when changes occur to the state container.

    Args:
        store: Pydux store
        loop: urwid MainLoop instance

    Returns:
        a pydux unsubscribe() function that will
        disconnect this listener when called.
    """
    last_state = [None]  # r/w closure
    get_state = store['get_state']

    def maybe_redraw():
        state = get_state()
        if not last_state[0] is state:
            last_state[0] = state
            loop.draw_screen()

    return store['subscribe'](maybe_redraw)
