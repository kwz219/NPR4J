package de.verygame.square.core.event;

import com.badlogic.gdx.Gdx;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import de.verygame.square.core.event.Event.EventType;

/**
 * @author Rico Schrage
 *
 * Emits events to all event-listeners.
 * <br>
 * Event can be received via annotation or {@link EventListener#handleEvent(Event, Object...)}.
 */
public class EventEmitter {

    /** List of all registered {@link EventListener}'s */
    private final Map<EventListener, List<EventType>> eventHandler;

    /**
     * Construct an event-emitter.
     */
    public EventEmitter() {
        this.eventHandler = new HashMap<>();
    }

    /**
     * Register an {@link EventListener} for a specific event type.
     *
     * @param eventListener {@link EventListener}, which should get registered
     */
    public void register(EventListener eventListener, EventType type) {
        if (eventHandler.containsKey(eventListener)) {
            eventHandler.get(eventListener).add(type);
        }
        else {
            final List<Event.EventType> list = new ArrayList<>(EventType.values().length);
            list.add(type);
            this.eventHandler.put(eventListener, list);
        }
    }

    /**
     * Unregister an {@link EventListener}.
     *
     * @param eventListener {@link EventListener}, which should get unregistered
     */
    public void unregister(EventListener eventListener, EventType type) {
        if (eventHandler.containsKey(eventListener)) {
            final List<EventType> list = eventHandler.get(eventListener);
            if (list.size() == 1) {
                eventHandler.remove(eventListener);
            }
            else {
                list.remove(type);
            }
        }
    }

    /**
     * Checks whether an {@link EventListener} is registered for a specific event type.
     *
     * @param eventListener listener, which should get checked.
     * @return true if the listener is already registered, false otherwise
     */
    public boolean isRegistered(EventListener eventListener, EventType eventType) {
        return eventHandler.containsKey(eventListener)
                && eventHandler.get(eventListener).contains(eventType);
    }

    /**
     * Emits an event to all listeners, which are registered for the specific event type. The events can either be received via {@link EventListener#handleEvent(Event, Object...)} or
     * with the help of annotations {@link EventRoute}.
     * <br>
     * Hint: Every event will only be delivered once!
     *
     * @param event type of the event
     * @param attachedObjects objects, which are related to the update.
     * @see Event
     */
    public void emitEvent(Event event, Object... attachedObjects) {
        for (Map.Entry<EventListener, List<EventType>> entry : eventHandler.entrySet()) {
            final EventListener eventListener = entry.getKey();
            final boolean sendEvent = entry.getValue().contains(event.getType());
            if (!emitReflectionEvent(eventListener, event, attachedObjects) && sendEvent) {
                eventListener.handleEvent(event, attachedObjects);
            }
        }
    }

    /**
     * Helper method, which emits the give event to the appropriate annotated method.
     *
     * @param target recipient of the event
     * @param event {@link Event}
     * @param attached attached objects
     * @return true if an appropriate method has been found, false otherwise
     */
    private boolean emitReflectionEvent(final EventListener target, final Event event, final Object... attached) {
        for (final Method method : target.getClass().getMethods()) {
            if (method.isAnnotationPresent(EventRoute.class) && method.getAnnotation(EventRoute.class).value() == event) {
                try {
                    method.invoke(target, attached);
                    return true;
                }
                catch (IllegalAccessException | IllegalArgumentException | InvocationTargetException e) {
                    Gdx.app.error(getClass().getSimpleName(), "An " + e.getClass().getSimpleName() + " has occurred. Reason: " + e.getMessage(), e);
                }
            }
        }
        return false;
    }

}
