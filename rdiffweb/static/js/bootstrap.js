/*!
  * Bootstrap v5.3.8 (https://getbootstrap.com/)
  * Copyright 2011-2023 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory(require('@popperjs/core')) :
  typeof define === 'function' && define.amd ? define(['@popperjs/core'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.bootstrap = factory(global.Popper));
})(this, (function (Popper) { 'use strict';

  function _interopNamespaceDefault(e) {
    const n = Object.create(null, { [Symbol.toStringTag]: { value: 'Module' } });
    if (e) {
      for (const k in e) {
        if (k !== 'default') {
          const d = Object.getOwnPropertyDescriptor(e, k);
          Object.defineProperty(n, k, d.get ? d : {
            enumerable: true,
            get: () => e[k]
          });
        }
      }
    }
    n.default = e;
    return Object.freeze(n);
  }

  const Popper__namespace = /*#__PURE__*/_interopNamespaceDefault(Popper);

  function _defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];
      descriptor.enumerable = descriptor.enumerable || false;
      descriptor.configurable = true;
      if ("value" in descriptor) descriptor.writable = true;
      Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor);
    }
  }
  function _createClass(Constructor, protoProps, staticProps) {
    if (protoProps) _defineProperties(Constructor.prototype, protoProps);
    if (staticProps) _defineProperties(Constructor, staticProps);
    Object.defineProperty(Constructor, "prototype", {
      writable: false
    });
    return Constructor;
  }
  function _extends() {
    _extends = Object.assign ? Object.assign.bind() : function (target) {
      for (var i = 1; i < arguments.length; i++) {
        var source = arguments[i];
        for (var key in source) {
          if (Object.prototype.hasOwnProperty.call(source, key)) {
            target[key] = source[key];
          }
        }
      }
      return target;
    };
    return _extends.apply(this, arguments);
  }
  function _inheritsLoose(subClass, superClass) {
    subClass.prototype = Object.create(superClass.prototype);
    subClass.prototype.constructor = subClass;
    _setPrototypeOf(subClass, superClass);
  }
  function _setPrototypeOf(o, p) {
    _setPrototypeOf = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function _setPrototypeOf(o, p) {
      o.__proto__ = p;
      return o;
    };
    return _setPrototypeOf(o, p);
  }
  function _assertThisInitialized(self) {
    if (self === void 0) {
      throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
    }
    return self;
  }
  function _unsupportedIterableToArray(o, minLen) {
    if (!o) return;
    if (typeof o === "string") return _arrayLikeToArray(o, minLen);
    var n = Object.prototype.toString.call(o).slice(8, -1);
    if (n === "Object" && o.constructor) n = o.constructor.name;
    if (n === "Map" || n === "Set") return Array.from(o);
    if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen);
  }
  function _arrayLikeToArray(arr, len) {
    if (len == null || len > arr.length) len = arr.length;
    for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
    return arr2;
  }
  function _createForOfIteratorHelperLoose(o, allowArrayLike) {
    var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"];
    if (it) return (it = it.call(o)).next.bind(it);
    if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") {
      if (it) o = it;
      var i = 0;
      return function () {
        if (i >= o.length) return {
          done: true
        };
        return {
          done: false,
          value: o[i++]
        };
      };
    }
    throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.");
  }
  function _toPrimitive(input, hint) {
    if (typeof input !== "object" || input === null) return input;
    var prim = input[Symbol.toPrimitive];
    if (prim !== undefined) {
      var res = prim.call(input, hint || "default");
      if (typeof res !== "object") return res;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return (hint === "string" ? String : Number)(input);
  }
  function _toPropertyKey(arg) {
    var key = _toPrimitive(arg, "string");
    return typeof key === "symbol" ? key : String(key);
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/data.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  /**
   * Constants
   */

  var elementMap = new Map();
  const Data = {
    set: function set(element, key, instance) {
      if (!elementMap.has(element)) {
        elementMap.set(element, new Map());
      }
      var instanceMap = elementMap.get(element);

      // make it clear we only want one instance per element
      // can be removed later when multiple key/instances are fine to be used
      if (!instanceMap.has(key) && instanceMap.size !== 0) {
        // eslint-disable-next-line no-console
        console.error("Bootstrap doesn't allow more than one instance per element. Bound instance: " + Array.from(instanceMap.keys())[0] + ".");
        return;
      }
      instanceMap.set(key, instance);
    },
    get: function get(element, key) {
      if (elementMap.has(element)) {
        return elementMap.get(element).get(key) || null;
      }
      return null;
    },
    remove: function remove(element, key) {
      if (!elementMap.has(element)) {
        return;
      }
      var instanceMap = elementMap.get(element);
      instanceMap["delete"](key);

      // free up element references if there are no instances left for an element
      if (instanceMap.size === 0) {
        elementMap["delete"](element);
      }
    }
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/index.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  var MAX_UID = 1000000;
  var MILLISECONDS_MULTIPLIER = 1000;
  var TRANSITION_END = 'transitionend';

  /**
   * Properly escape IDs selectors to handle weird IDs
   * @param {string} selector
   * @returns {string}
   */
  var parseSelector = function parseSelector(selector) {
    if (selector && window.CSS && window.CSS.escape) {
      // document.querySelector needs escaping to handle IDs (html5+) containing for instance /
      selector = selector.replace(/#([^\s"#']+)/g, function (match, id) {
        return "#" + CSS.escape(id);
      });
    }
    return selector;
  };

  // Shout-out Angus Croll (https://goo.gl/pxwQGp)
  var toType = function toType(object) {
    if (object === null || object === undefined) {
      return "" + object;
    }
    return Object.prototype.toString.call(object).match(/\s([a-z]+)/i)[1].toLowerCase();
  };

  /**
   * Public Util API
   */

  var getUID = function getUID(prefix) {
    do {
      prefix += Math.floor(Math.random() * MAX_UID);
    } while (document.getElementById(prefix));
    return prefix;
  };
  var getTransitionDurationFromElement = function getTransitionDurationFromElement(element) {
    if (!element) {
      return 0;
    }

    // Get transition-duration of the element
    var _window$getComputedSt = window.getComputedStyle(element),
      transitionDuration = _window$getComputedSt.transitionDuration,
      transitionDelay = _window$getComputedSt.transitionDelay;
    var floatTransitionDuration = Number.parseFloat(transitionDuration);
    var floatTransitionDelay = Number.parseFloat(transitionDelay);

    // Return 0 if element or transition duration is not found
    if (!floatTransitionDuration && !floatTransitionDelay) {
      return 0;
    }

    // If multiple durations are defined, take the first
    transitionDuration = transitionDuration.split(',')[0];
    transitionDelay = transitionDelay.split(',')[0];
    return (Number.parseFloat(transitionDuration) + Number.parseFloat(transitionDelay)) * MILLISECONDS_MULTIPLIER;
  };
  var triggerTransitionEnd = function triggerTransitionEnd(element) {
    element.dispatchEvent(new Event(TRANSITION_END));
  };
  var isElement = function isElement(object) {
    if (!object || typeof object !== 'object') {
      return false;
    }
    if (typeof object.jquery !== 'undefined') {
      object = object[0];
    }
    return typeof object.nodeType !== 'undefined';
  };
  var getElement = function getElement(object) {
    // it's a jQuery object or a node element
    if (isElement(object)) {
      return object.jquery ? object[0] : object;
    }
    if (typeof object === 'string' && object.length > 0) {
      return document.querySelector(parseSelector(object));
    }
    return null;
  };
  var isVisible = function isVisible(element) {
    if (!isElement(element) || element.getClientRects().length === 0) {
      return false;
    }
    var elementIsVisible = getComputedStyle(element).getPropertyValue('visibility') === 'visible';
    // Handle `details` element as its content may falsie appear visible when it is closed
    var closedDetails = element.closest('details:not([open])');
    if (!closedDetails) {
      return elementIsVisible;
    }
    if (closedDetails !== element) {
      var summary = element.closest('summary');
      if (summary && summary.parentNode !== closedDetails) {
        return false;
      }
      if (summary === null) {
        return false;
      }
    }
    return elementIsVisible;
  };
  var isDisabled = function isDisabled(element) {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) {
      return true;
    }
    if (element.classList.contains('disabled')) {
      return true;
    }
    if (typeof element.disabled !== 'undefined') {
      return element.disabled;
    }
    return element.hasAttribute('disabled') && element.getAttribute('disabled') !== 'false';
  };
  var findShadowRoot = function findShadowRoot(element) {
    if (!document.documentElement.attachShadow) {
      return null;
    }

    // Can find the shadow root otherwise it'll return the document
    if (typeof element.getRootNode === 'function') {
      var root = element.getRootNode();
      return root instanceof ShadowRoot ? root : null;
    }
    if (element instanceof ShadowRoot) {
      return element;
    }

    // when we don't find a shadow root
    if (!element.parentNode) {
      return null;
    }
    return findShadowRoot(element.parentNode);
  };
  var noop = function noop() {};

  /**
   * Trick to restart an element's animation
   *
   * @param {HTMLElement} element
   * @return void
   *
   * @see https://www.harrytheo.com/blog/2021/02/restart-a-css-animation-with-javascript/#restarting-a-css-animation
   */
  var reflow = function reflow(element) {
    element.offsetHeight; // eslint-disable-line no-unused-expressions
  };

  var getjQuery = function getjQuery() {
    if (window.jQuery && !document.body.hasAttribute('data-bs-no-jquery')) {
      return window.jQuery;
    }
    return null;
  };
  var DOMContentLoadedCallbacks = [];
  var onDOMContentLoaded = function onDOMContentLoaded(callback) {
    if (document.readyState === 'loading') {
      // add listener on the first call when the document is in loading state
      if (!DOMContentLoadedCallbacks.length) {
        document.addEventListener('DOMContentLoaded', function () {
          for (var _i = 0, _DOMContentLoadedCall = DOMContentLoadedCallbacks; _i < _DOMContentLoadedCall.length; _i++) {
            var _callback = _DOMContentLoadedCall[_i];
            _callback();
          }
        });
      }
      DOMContentLoadedCallbacks.push(callback);
    } else {
      callback();
    }
  };
  var isRTL = function isRTL() {
    return document.documentElement.dir === 'rtl';
  };
  var defineJQueryPlugin = function defineJQueryPlugin(plugin) {
    onDOMContentLoaded(function () {
      var $ = getjQuery();
      /* istanbul ignore if */
      if ($) {
        var name = plugin.NAME;
        var JQUERY_NO_CONFLICT = $.fn[name];
        $.fn[name] = plugin.jQueryInterface;
        $.fn[name].Constructor = plugin;
        $.fn[name].noConflict = function () {
          $.fn[name] = JQUERY_NO_CONFLICT;
          return plugin.jQueryInterface;
        };
      }
    });
  };
  var execute = function execute(possibleCallback, args, defaultValue) {
    if (args === void 0) {
      args = [];
    }
    if (defaultValue === void 0) {
      defaultValue = possibleCallback;
    }
    return typeof possibleCallback === 'function' ? possibleCallback.call.apply(possibleCallback, args) : defaultValue;
  };
  var executeAfterTransition = function executeAfterTransition(callback, transitionElement, waitForTransition) {
    if (waitForTransition === void 0) {
      waitForTransition = true;
    }
    if (!waitForTransition) {
      execute(callback);
      return;
    }
    var durationPadding = 5;
    var emulatedDuration = getTransitionDurationFromElement(transitionElement) + durationPadding;
    var called = false;
    var handler = function handler(_ref) {
      var target = _ref.target;
      if (target !== transitionElement) {
        return;
      }
      called = true;
      transitionElement.removeEventListener(TRANSITION_END, handler);
      execute(callback);
    };
    transitionElement.addEventListener(TRANSITION_END, handler);
    setTimeout(function () {
      if (!called) {
        triggerTransitionEnd(transitionElement);
      }
    }, emulatedDuration);
  };

  /**
   * Return the previous/next element of a list.
   *
   * @param {array} list    The list of elements
   * @param activeElement   The active element
   * @param shouldGetNext   Choose to get next or previous element
   * @param isCycleAllowed
   * @return {Element|elem} The proper element
   */
  var getNextActiveElement = function getNextActiveElement(list, activeElement, shouldGetNext, isCycleAllowed) {
    var listLength = list.length;
    var index = list.indexOf(activeElement);

    // if the element does not exist in the list return an element
    // depending on the direction and if cycle is allowed
    if (index === -1) {
      return !shouldGetNext && isCycleAllowed ? list[listLength - 1] : list[0];
    }
    index += shouldGetNext ? 1 : -1;
    if (isCycleAllowed) {
      index = (index + listLength) % listLength;
    }
    return list[Math.max(0, Math.min(index, listLength - 1))];
  };

  /**
   * Constants
   */

  var namespaceRegex = /[^.]*(?=\..*)\.|.*/;
  var stripNameRegex = /\..*/;
  var stripUidRegex = /::\d+$/;
  var eventRegistry = {}; // Events storage
  var uidEvent = 1;
  var customEvents = {
    mouseenter: 'mouseover',
    mouseleave: 'mouseout'
  };
  var nativeEvents = new Set(['click', 'dblclick', 'mouseup', 'mousedown', 'contextmenu', 'mousewheel', 'DOMMouseScroll', 'mouseover', 'mouseout', 'mousemove', 'selectstart', 'selectend', 'keydown', 'keypress', 'keyup', 'orientationchange', 'touchstart', 'touchmove', 'touchend', 'touchcancel', 'pointerdown', 'pointermove', 'pointerup', 'pointerleave', 'pointercancel', 'gesturestart', 'gesturechange', 'gestureend', 'focus', 'blur', 'change', 'reset', 'select', 'submit', 'focusin', 'focusout', 'load', 'unload', 'beforeunload', 'resize', 'move', 'DOMContentLoaded', 'readystatechange', 'error', 'abort', 'scroll']);

  /**
   * Private methods
   */

  function makeEventUid(element, uid) {
    return uid && uid + "::" + uidEvent++ || element.uidEvent || uidEvent++;
  }
  function getElementEvents(element) {
    var uid = makeEventUid(element);
    element.uidEvent = uid;
    eventRegistry[uid] = eventRegistry[uid] || {};
    return eventRegistry[uid];
  }
  function bootstrapHandler(element, fn) {
    return function handler(event) {
      hydrateObj(event, {
        delegateTarget: element
      });
      if (handler.oneOff) {
        EventHandler.off(element, event.type, fn);
      }
      return fn.apply(element, [event]);
    };
  }
  function bootstrapDelegationHandler(element, selector, fn) {
    return function handler(event) {
      var domElements = element.querySelectorAll(selector);
      for (var target = event.target; target && target !== this; target = target.parentNode) {
        for (var _iterator = _createForOfIteratorHelperLoose(domElements), _step; !(_step = _iterator()).done;) {
          var domElement = _step.value;
          if (domElement !== target) {
            continue;
          }
          hydrateObj(event, {
            delegateTarget: target
          });
          if (handler.oneOff) {
            EventHandler.off(element, event.type, selector, fn);
          }
          return fn.apply(target, [event]);
        }
      }
    };
  }
  function findHandler(events, callable, delegationSelector) {
    if (delegationSelector === void 0) {
      delegationSelector = null;
    }
    return Object.values(events).find(function (event) {
      return event.callable === callable && event.delegationSelector === delegationSelector;
    });
  }
  function normalizeParameters(originalTypeEvent, handler, delegationFunction) {
    var isDelegated = typeof handler === 'string';
    // TODO: tooltip passes `false` instead of selector, so we need to check
    var callable = isDelegated ? delegationFunction : handler || delegationFunction;
    var typeEvent = getTypeEvent(originalTypeEvent);
    if (!nativeEvents.has(typeEvent)) {
      typeEvent = originalTypeEvent;
    }
    return [isDelegated, callable, typeEvent];
  }
  function addHandler(element, originalTypeEvent, handler, delegationFunction, oneOff) {
    if (typeof originalTypeEvent !== 'string' || !element) {
      return;
    }
    var _normalizeParameters = normalizeParameters(originalTypeEvent, handler, delegationFunction),
      isDelegated = _normalizeParameters[0],
      callable = _normalizeParameters[1],
      typeEvent = _normalizeParameters[2];

    // in case of mouseenter or mouseleave wrap the handler within a function that checks for its DOM position
    // this prevents the handler from being dispatched the same way as mouseover or mouseout does
    if (originalTypeEvent in customEvents) {
      var wrapFunction = function wrapFunction(fn) {
        return function (event) {
          if (!event.relatedTarget || event.relatedTarget !== event.delegateTarget && !event.delegateTarget.contains(event.relatedTarget)) {
            return fn.call(this, event);
          }
        };
      };
      callable = wrapFunction(callable);
    }
    var events = getElementEvents(element);
    var handlers = events[typeEvent] || (events[typeEvent] = {});
    var previousFunction = findHandler(handlers, callable, isDelegated ? handler : null);
    if (previousFunction) {
      previousFunction.oneOff = previousFunction.oneOff && oneOff;
      return;
    }
    var uid = makeEventUid(callable, originalTypeEvent.replace(namespaceRegex, ''));
    var fn = isDelegated ? bootstrapDelegationHandler(element, handler, callable) : bootstrapHandler(element, callable);
    fn.delegationSelector = isDelegated ? handler : null;
    fn.callable = callable;
    fn.oneOff = oneOff;
    fn.uidEvent = uid;
    handlers[uid] = fn;
    element.addEventListener(typeEvent, fn, isDelegated);
  }
  function removeHandler(element, events, typeEvent, handler, delegationSelector) {
    var fn = findHandler(events[typeEvent], handler, delegationSelector);
    if (!fn) {
      return;
    }
    element.removeEventListener(typeEvent, fn, Boolean(delegationSelector));
    delete events[typeEvent][fn.uidEvent];
  }
  function removeNamespacedHandlers(element, events, typeEvent, namespace) {
    var storeElementEvent = events[typeEvent] || {};
    for (var _i = 0, _Object$entries = Object.entries(storeElementEvent); _i < _Object$entries.length; _i++) {
      var _Object$entries$_i = _Object$entries[_i],
        handlerKey = _Object$entries$_i[0],
        event = _Object$entries$_i[1];
      if (handlerKey.includes(namespace)) {
        removeHandler(element, events, typeEvent, event.callable, event.delegationSelector);
      }
    }
  }
  function getTypeEvent(event) {
    // allow to get the native events from namespaced events ('click.bs.button' --> 'click')
    event = event.replace(stripNameRegex, '');
    return customEvents[event] || event;
  }
  var EventHandler = {
    on: function on(element, event, handler, delegationFunction) {
      addHandler(element, event, handler, delegationFunction, false);
    },
    one: function one(element, event, handler, delegationFunction) {
      addHandler(element, event, handler, delegationFunction, true);
    },
    off: function off(element, originalTypeEvent, handler, delegationFunction) {
      if (typeof originalTypeEvent !== 'string' || !element) {
        return;
      }
      var _normalizeParameters2 = normalizeParameters(originalTypeEvent, handler, delegationFunction),
        isDelegated = _normalizeParameters2[0],
        callable = _normalizeParameters2[1],
        typeEvent = _normalizeParameters2[2];
      var inNamespace = typeEvent !== originalTypeEvent;
      var events = getElementEvents(element);
      var storeElementEvent = events[typeEvent] || {};
      var isNamespace = originalTypeEvent.startsWith('.');
      if (typeof callable !== 'undefined') {
        // Simplest case: handler is passed, remove that listener ONLY.
        if (!Object.keys(storeElementEvent).length) {
          return;
        }
        removeHandler(element, events, typeEvent, callable, isDelegated ? handler : null);
        return;
      }
      if (isNamespace) {
        for (var _i2 = 0, _Object$keys = Object.keys(events); _i2 < _Object$keys.length; _i2++) {
          var elementEvent = _Object$keys[_i2];
          removeNamespacedHandlers(element, events, elementEvent, originalTypeEvent.slice(1));
        }
      }
      for (var _i3 = 0, _Object$entries2 = Object.entries(storeElementEvent); _i3 < _Object$entries2.length; _i3++) {
        var _Object$entries2$_i = _Object$entries2[_i3],
          keyHandlers = _Object$entries2$_i[0],
          event = _Object$entries2$_i[1];
        var handlerKey = keyHandlers.replace(stripUidRegex, '');
        if (!inNamespace || originalTypeEvent.includes(handlerKey)) {
          removeHandler(element, events, typeEvent, event.callable, event.delegationSelector);
        }
      }
    },
    trigger: function trigger(element, event, args) {
      if (typeof event !== 'string' || !element) {
        return null;
      }
      var $ = getjQuery();
      var typeEvent = getTypeEvent(event);
      var inNamespace = event !== typeEvent;
      var jQueryEvent = null;
      var bubbles = true;
      var nativeDispatch = true;
      var defaultPrevented = false;
      if (inNamespace && $) {
        jQueryEvent = $.Event(event, args);
        $(element).trigger(jQueryEvent);
        bubbles = !jQueryEvent.isPropagationStopped();
        nativeDispatch = !jQueryEvent.isImmediatePropagationStopped();
        defaultPrevented = jQueryEvent.isDefaultPrevented();
      }
      var evt = hydrateObj(new Event(event, {
        bubbles: bubbles,
        cancelable: true
      }), args);
      if (defaultPrevented) {
        evt.preventDefault();
      }
      if (nativeDispatch) {
        element.dispatchEvent(evt);
      }
      if (evt.defaultPrevented && jQueryEvent) {
        jQueryEvent.preventDefault();
      }
      return evt;
    }
  };
  function hydrateObj(obj, meta) {
    if (meta === void 0) {
      meta = {};
    }
    var _loop = function _loop() {
      var _Object$entries3$_i = _Object$entries3[_i4],
        key = _Object$entries3$_i[0],
        value = _Object$entries3$_i[1];
      try {
        obj[key] = value;
      } catch (_unused) {
        Object.defineProperty(obj, key, {
          configurable: true,
          get: function get() {
            return value;
          }
        });
      }
    };
    for (var _i4 = 0, _Object$entries3 = Object.entries(meta); _i4 < _Object$entries3.length; _i4++) {
      _loop();
    }
    return obj;
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/manipulator.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  function normalizeData(value) {
    if (value === 'true') {
      return true;
    }
    if (value === 'false') {
      return false;
    }
    if (value === Number(value).toString()) {
      return Number(value);
    }
    if (value === '' || value === 'null') {
      return null;
    }
    if (typeof value !== 'string') {
      return value;
    }
    try {
      return JSON.parse(decodeURIComponent(value));
    } catch (_unused) {
      return value;
    }
  }
  function normalizeDataKey(key) {
    return key.replace(/[A-Z]/g, function (chr) {
      return "-" + chr.toLowerCase();
    });
  }
  var Manipulator = {
    setDataAttribute: function setDataAttribute(element, key, value) {
      element.setAttribute("data-bs-" + normalizeDataKey(key), value);
    },
    removeDataAttribute: function removeDataAttribute(element, key) {
      element.removeAttribute("data-bs-" + normalizeDataKey(key));
    },
    getDataAttributes: function getDataAttributes(element) {
      if (!element) {
        return {};
      }
      var attributes = {};
      var bsKeys = Object.keys(element.dataset).filter(function (key) {
        return key.startsWith('bs') && !key.startsWith('bsConfig');
      });
      for (var _iterator = _createForOfIteratorHelperLoose(bsKeys), _step; !(_step = _iterator()).done;) {
        var key = _step.value;
        var pureKey = key.replace(/^bs/, '');
        pureKey = pureKey.charAt(0).toLowerCase() + pureKey.slice(1);
        attributes[pureKey] = normalizeData(element.dataset[key]);
      }
      return attributes;
    },
    getDataAttribute: function getDataAttribute(element, key) {
      return normalizeData(element.getAttribute("data-bs-" + normalizeDataKey(key)));
    }
  };

  /**
   * Class definition
   */
  var Config = /*#__PURE__*/function () {
    function Config() {}
    var _proto = Config.prototype;
    _proto._getConfig = function _getConfig(config) {
      config = this._mergeConfigObj(config);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    };
    _proto._configAfterMerge = function _configAfterMerge(config) {
      return config;
    };
    _proto._mergeConfigObj = function _mergeConfigObj(config, element) {
      var jsonConfig = isElement(element) ? Manipulator.getDataAttribute(element, 'config') : {}; // try to parse

      return _extends({}, this.constructor.Default, typeof jsonConfig === 'object' ? jsonConfig : {}, isElement(element) ? Manipulator.getDataAttributes(element) : {}, typeof config === 'object' ? config : {});
    };
    _proto._typeCheckConfig = function _typeCheckConfig(config, configTypes) {
      if (configTypes === void 0) {
        configTypes = this.constructor.DefaultType;
      }
      for (var _i = 0, _Object$entries = Object.entries(configTypes); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = _Object$entries[_i],
          property = _Object$entries$_i[0],
          expectedTypes = _Object$entries$_i[1];
        var value = config[property];
        var valueType = isElement(value) ? 'element' : toType(value);
        if (!new RegExp(expectedTypes).test(valueType)) {
          throw new TypeError(this.constructor.NAME.toUpperCase() + ": Option \"" + property + "\" provided type \"" + valueType + "\" but expected type \"" + expectedTypes + "\".");
        }
      }
    };
    _createClass(Config, null, [{
      key: "Default",
      get:
      // Getters
      function get() {
        return {};
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return {};
      }
    }, {
      key: "NAME",
      get: function get() {
        throw new Error('You have to implement the static method "NAME", for each component!');
      }
    }]);
    return Config;
  }();

  /**
   * Constants
   */

  var VERSION = '5.3.8';

  /**
   * Class definition
   */
  var BaseComponent = /*#__PURE__*/function (_Config) {
    _inheritsLoose(BaseComponent, _Config);
    function BaseComponent(element, config) {
      var _this;
      _this = _Config.call(this) || this;
      element = getElement(element);
      if (!element) {
        return _assertThisInitialized(_this);
      }
      _this._element = element;
      _this._config = _this._getConfig(config);
      Data.set(_this._element, _this.constructor.DATA_KEY, _assertThisInitialized(_this));
      return _this;
    }

    // Public
    var _proto = BaseComponent.prototype;
    _proto.dispose = function dispose() {
      Data.remove(this._element, this.constructor.DATA_KEY);
      EventHandler.off(this._element, this.constructor.EVENT_KEY);
      for (var _iterator = _createForOfIteratorHelperLoose(Object.getOwnPropertyNames(this)), _step; !(_step = _iterator()).done;) {
        var propertyName = _step.value;
        this[propertyName] = null;
      }
    }

    // Private
    ;
    _proto._queueCallback = function _queueCallback(callback, element, isAnimated) {
      if (isAnimated === void 0) {
        isAnimated = true;
      }
      executeAfterTransition(callback, element, isAnimated);
    };
    _proto._getConfig = function _getConfig(config) {
      config = this._mergeConfigObj(config, this._element);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    }

    // Static
    ;
    BaseComponent.getInstance = function getInstance(element) {
      return Data.get(getElement(element), this.DATA_KEY);
    };
    BaseComponent.getOrCreateInstance = function getOrCreateInstance(element, config) {
      if (config === void 0) {
        config = {};
      }
      return this.getInstance(element) || new this(element, typeof config === 'object' ? config : null);
    };
    BaseComponent.eventName = function eventName(name) {
      return "" + name + this.EVENT_KEY;
    };
    _createClass(BaseComponent, null, [{
      key: "VERSION",
      get: function get() {
        return VERSION;
      }
    }, {
      key: "DATA_KEY",
      get: function get() {
        return "bs." + this.NAME;
      }
    }, {
      key: "EVENT_KEY",
      get: function get() {
        return "." + this.DATA_KEY;
      }
    }]);
    return BaseComponent;
  }(Config);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/selector-engine.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  var getSelector = function getSelector(element) {
    var selector = element.getAttribute('data-bs-target');
    if (!selector || selector === '#') {
      var hrefAttribute = element.getAttribute('href');

      // The only valid content that could double as a selector are IDs or classes,
      // so everything starting with `#` or `.`. If a "real" URL is used as the selector,
      // `document.querySelector` will rightfully complain it is invalid.
      // See https://github.com/twbs/bootstrap/issues/32273
      if (!hrefAttribute || !hrefAttribute.includes('#') && !hrefAttribute.startsWith('.')) {
        return null;
      }

      // Just in case some CMS puts out a full URL with the anchor appended
      if (hrefAttribute.includes('#') && !hrefAttribute.startsWith('#')) {
        hrefAttribute = "#" + hrefAttribute.split('#')[1];
      }
      selector = hrefAttribute && hrefAttribute !== '#' ? hrefAttribute.trim() : null;
    }
    return selector ? selector.split(',').map(function (sel) {
      return parseSelector(sel);
    }).join(',') : null;
  };
  var SelectorEngine = {
    find: function find(selector, element) {
      var _ref;
      if (element === void 0) {
        element = document.documentElement;
      }
      return (_ref = []).concat.apply(_ref, Element.prototype.querySelectorAll.call(element, selector));
    },
    findOne: function findOne(selector, element) {
      if (element === void 0) {
        element = document.documentElement;
      }
      return Element.prototype.querySelector.call(element, selector);
    },
    children: function children(element, selector) {
      var _ref2;
      return (_ref2 = []).concat.apply(_ref2, element.children).filter(function (child) {
        return child.matches(selector);
      });
    },
    parents: function parents(element, selector) {
      var parents = [];
      var ancestor = element.parentNode.closest(selector);
      while (ancestor) {
        parents.push(ancestor);
        ancestor = ancestor.parentNode.closest(selector);
      }
      return parents;
    },
    prev: function prev(element, selector) {
      var previous = element.previousElementSibling;
      while (previous) {
        if (previous.matches(selector)) {
          return [previous];
        }
        previous = previous.previousElementSibling;
      }
      return [];
    },
    // TODO: this is now unused; remove later along with prev()
    next: function next(element, selector) {
      var next = element.nextElementSibling;
      while (next) {
        if (next.matches(selector)) {
          return [next];
        }
        next = next.nextElementSibling;
      }
      return [];
    },
    focusableChildren: function focusableChildren(element) {
      var focusables = ['a', 'button', 'input', 'textarea', 'select', 'details', '[tabindex]', '[contenteditable="true"]'].map(function (selector) {
        return selector + ":not([tabindex^=\"-\"])";
      }).join(',');
      return this.find(focusables, element).filter(function (el) {
        return !isDisabled(el) && isVisible(el);
      });
    },
    getSelectorFromElement: function getSelectorFromElement(element) {
      var selector = getSelector(element);
      if (selector) {
        return SelectorEngine.findOne(selector) ? selector : null;
      }
      return null;
    },
    getElementFromSelector: function getElementFromSelector(element) {
      var selector = getSelector(element);
      return selector ? SelectorEngine.findOne(selector) : null;
    },
    getMultipleElementsFromSelector: function getMultipleElementsFromSelector(element) {
      var selector = getSelector(element);
      return selector ? SelectorEngine.find(selector) : [];
    }
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/component-functions.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  var enableDismissTrigger = function enableDismissTrigger(component, method) {
    if (method === void 0) {
      method = 'hide';
    }
    var clickEvent = "click.dismiss" + component.EVENT_KEY;
    var name = component.NAME;
    EventHandler.on(document, clickEvent, "[data-bs-dismiss=\"" + name + "\"]", function (event) {
      if (['A', 'AREA'].includes(this.tagName)) {
        event.preventDefault();
      }
      if (isDisabled(this)) {
        return;
      }
      var target = SelectorEngine.getElementFromSelector(this) || this.closest("." + name);
      var instance = component.getOrCreateInstance(target);

      // Method argument is left, for Alert and only, as it doesn't implement the 'hide' method
      instance[method]();
    });
  };

  /**
   * Constants
   */

  var NAME$f = 'alert';
  var DATA_KEY$a = 'bs.alert';
  var EVENT_KEY$b = "." + DATA_KEY$a;
  var EVENT_CLOSE = "close" + EVENT_KEY$b;
  var EVENT_CLOSED = "closed" + EVENT_KEY$b;
  var CLASS_NAME_FADE$5 = 'fade';
  var CLASS_NAME_SHOW$8 = 'show';

  /**
   * Class definition
   */
  var Alert = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Alert, _BaseComponent);
    function Alert() {
      return _BaseComponent.apply(this, arguments) || this;
    }
    var _proto = Alert.prototype;
    // Public
    _proto.close = function close() {
      var _this = this;
      var closeEvent = EventHandler.trigger(this._element, EVENT_CLOSE);
      if (closeEvent.defaultPrevented) {
        return;
      }
      this._element.classList.remove(CLASS_NAME_SHOW$8);
      var isAnimated = this._element.classList.contains(CLASS_NAME_FADE$5);
      this._queueCallback(function () {
        return _this._destroyElement();
      }, this._element, isAnimated);
    }

    // Private
    ;
    _proto._destroyElement = function _destroyElement() {
      this._element.remove();
      EventHandler.trigger(this._element, EVENT_CLOSED);
      this.dispose();
    }

    // Static
    ;
    Alert.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Alert.getOrCreateInstance(this);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config](this);
      });
    };
    _createClass(Alert, null, [{
      key: "NAME",
      get:
      // Getters
      function get() {
        return NAME$f;
      }
    }]);
    return Alert;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  enableDismissTrigger(Alert, 'close');

  /**
   * jQuery
   */

  defineJQueryPlugin(Alert);

  /**
   * Constants
   */

  var NAME$e = 'button';
  var DATA_KEY$9 = 'bs.button';
  var EVENT_KEY$a = "." + DATA_KEY$9;
  var DATA_API_KEY$6 = '.data-api';
  var CLASS_NAME_ACTIVE$3 = 'active';
  var SELECTOR_DATA_TOGGLE$5 = '[data-bs-toggle="button"]';
  var EVENT_CLICK_DATA_API$6 = "click" + EVENT_KEY$a + DATA_API_KEY$6;

  /**
   * Class definition
   */
  var Button = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Button, _BaseComponent);
    function Button() {
      return _BaseComponent.apply(this, arguments) || this;
    }
    var _proto = Button.prototype;
    // Public
    _proto.toggle = function toggle() {
      // Toggle class and sync the `aria-pressed` attribute with the return value of the `.toggle()` method
      this._element.setAttribute('aria-pressed', this._element.classList.toggle(CLASS_NAME_ACTIVE$3));
    }

    // Static
    ;
    Button.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Button.getOrCreateInstance(this);
        if (config === 'toggle') {
          data[config]();
        }
      });
    };
    _createClass(Button, null, [{
      key: "NAME",
      get:
      // Getters
      function get() {
        return NAME$e;
      }
    }]);
    return Button;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API$6, SELECTOR_DATA_TOGGLE$5, function (event) {
    event.preventDefault();
    var button = event.target.closest(SELECTOR_DATA_TOGGLE$5);
    var data = Button.getOrCreateInstance(button);
    data.toggle();
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Button);

  /**
   * Constants
   */

  var NAME$d = 'swipe';
  var EVENT_KEY$9 = '.bs.swipe';
  var EVENT_TOUCHSTART = "touchstart" + EVENT_KEY$9;
  var EVENT_TOUCHMOVE = "touchmove" + EVENT_KEY$9;
  var EVENT_TOUCHEND = "touchend" + EVENT_KEY$9;
  var EVENT_POINTERDOWN = "pointerdown" + EVENT_KEY$9;
  var EVENT_POINTERUP = "pointerup" + EVENT_KEY$9;
  var POINTER_TYPE_TOUCH = 'touch';
  var POINTER_TYPE_PEN = 'pen';
  var CLASS_NAME_POINTER_EVENT = 'pointer-event';
  var SWIPE_THRESHOLD = 40;
  var Default$c = {
    endCallback: null,
    leftCallback: null,
    rightCallback: null
  };
  var DefaultType$c = {
    endCallback: '(function|null)',
    leftCallback: '(function|null)',
    rightCallback: '(function|null)'
  };

  /**
   * Class definition
   */
  var Swipe = /*#__PURE__*/function (_Config) {
    _inheritsLoose(Swipe, _Config);
    function Swipe(element, config) {
      var _this;
      _this = _Config.call(this) || this;
      _this._element = element;
      if (!element || !Swipe.isSupported()) {
        return _assertThisInitialized(_this);
      }
      _this._config = _this._getConfig(config);
      _this._deltaX = 0;
      _this._supportPointerEvents = Boolean(window.PointerEvent);
      _this._initEvents();
      return _this;
    }

    // Getters
    var _proto = Swipe.prototype;
    // Public
    _proto.dispose = function dispose() {
      EventHandler.off(this._element, EVENT_KEY$9);
    }

    // Private
    ;
    _proto._start = function _start(event) {
      if (!this._supportPointerEvents) {
        this._deltaX = event.touches[0].clientX;
        return;
      }
      if (this._eventIsPointerPenTouch(event)) {
        this._deltaX = event.clientX;
      }
    };
    _proto._end = function _end(event) {
      if (this._eventIsPointerPenTouch(event)) {
        this._deltaX = event.clientX - this._deltaX;
      }
      this._handleSwipe();
      execute(this._config.endCallback);
    };
    _proto._move = function _move(event) {
      this._deltaX = event.touches && event.touches.length > 1 ? 0 : event.touches[0].clientX - this._deltaX;
    };
    _proto._handleSwipe = function _handleSwipe() {
      var absDeltaX = Math.abs(this._deltaX);
      if (absDeltaX <= SWIPE_THRESHOLD) {
        return;
      }
      var direction = absDeltaX / this._deltaX;
      this._deltaX = 0;
      if (!direction) {
        return;
      }
      execute(direction > 0 ? this._config.rightCallback : this._config.leftCallback);
    };
    _proto._initEvents = function _initEvents() {
      var _this2 = this;
      if (this._supportPointerEvents) {
        EventHandler.on(this._element, EVENT_POINTERDOWN, function (event) {
          return _this2._start(event);
        });
        EventHandler.on(this._element, EVENT_POINTERUP, function (event) {
          return _this2._end(event);
        });
        this._element.classList.add(CLASS_NAME_POINTER_EVENT);
      } else {
        EventHandler.on(this._element, EVENT_TOUCHSTART, function (event) {
          return _this2._start(event);
        });
        EventHandler.on(this._element, EVENT_TOUCHMOVE, function (event) {
          return _this2._move(event);
        });
        EventHandler.on(this._element, EVENT_TOUCHEND, function (event) {
          return _this2._end(event);
        });
      }
    };
    _proto._eventIsPointerPenTouch = function _eventIsPointerPenTouch(event) {
      return this._supportPointerEvents && (event.pointerType === POINTER_TYPE_PEN || event.pointerType === POINTER_TYPE_TOUCH);
    }

    // Static
    ;
    Swipe.isSupported = function isSupported() {
      return 'ontouchstart' in document.documentElement || navigator.maxTouchPoints > 0;
    };
    _createClass(Swipe, null, [{
      key: "Default",
      get: function get() {
        return Default$c;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$c;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$d;
      }
    }]);
    return Swipe;
  }(Config);

  var _KEY_TO_DIRECTION;

  /**
   * Constants
   */

  var NAME$c = 'carousel';
  var DATA_KEY$8 = 'bs.carousel';
  var EVENT_KEY$8 = "." + DATA_KEY$8;
  var DATA_API_KEY$5 = '.data-api';
  var ARROW_LEFT_KEY$1 = 'ArrowLeft';
  var ARROW_RIGHT_KEY$1 = 'ArrowRight';
  var TOUCHEVENT_COMPAT_WAIT = 500; // Time for mouse compat events to fire after touch

  var ORDER_NEXT = 'next';
  var ORDER_PREV = 'prev';
  var DIRECTION_LEFT = 'left';
  var DIRECTION_RIGHT = 'right';
  var EVENT_SLIDE = "slide" + EVENT_KEY$8;
  var EVENT_SLID = "slid" + EVENT_KEY$8;
  var EVENT_KEYDOWN$1 = "keydown" + EVENT_KEY$8;
  var EVENT_MOUSEENTER$1 = "mouseenter" + EVENT_KEY$8;
  var EVENT_MOUSELEAVE$1 = "mouseleave" + EVENT_KEY$8;
  var EVENT_DRAG_START = "dragstart" + EVENT_KEY$8;
  var EVENT_LOAD_DATA_API$3 = "load" + EVENT_KEY$8 + DATA_API_KEY$5;
  var EVENT_CLICK_DATA_API$5 = "click" + EVENT_KEY$8 + DATA_API_KEY$5;
  var CLASS_NAME_CAROUSEL = 'carousel';
  var CLASS_NAME_ACTIVE$2 = 'active';
  var CLASS_NAME_SLIDE = 'slide';
  var CLASS_NAME_END = 'carousel-item-end';
  var CLASS_NAME_START = 'carousel-item-start';
  var CLASS_NAME_NEXT = 'carousel-item-next';
  var CLASS_NAME_PREV = 'carousel-item-prev';
  var SELECTOR_ACTIVE = '.active';
  var SELECTOR_ITEM = '.carousel-item';
  var SELECTOR_ACTIVE_ITEM = SELECTOR_ACTIVE + SELECTOR_ITEM;
  var SELECTOR_ITEM_IMG = '.carousel-item img';
  var SELECTOR_INDICATORS = '.carousel-indicators';
  var SELECTOR_DATA_SLIDE = '[data-bs-slide], [data-bs-slide-to]';
  var SELECTOR_DATA_RIDE = '[data-bs-ride="carousel"]';
  var KEY_TO_DIRECTION = (_KEY_TO_DIRECTION = {}, _KEY_TO_DIRECTION[ARROW_LEFT_KEY$1] = DIRECTION_RIGHT, _KEY_TO_DIRECTION[ARROW_RIGHT_KEY$1] = DIRECTION_LEFT, _KEY_TO_DIRECTION);
  var Default$b = {
    interval: 5000,
    keyboard: true,
    pause: 'hover',
    ride: false,
    touch: true,
    wrap: true
  };
  var DefaultType$b = {
    interval: '(number|boolean)',
    // TODO:v6 remove boolean support
    keyboard: 'boolean',
    pause: '(string|boolean)',
    ride: '(boolean|string)',
    touch: 'boolean',
    wrap: 'boolean'
  };

  /**
   * Class definition
   */
  var Carousel = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Carousel, _BaseComponent);
    function Carousel(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._interval = null;
      _this._activeElement = null;
      _this._isSliding = false;
      _this.touchTimeout = null;
      _this._swipeHelper = null;
      _this._indicatorsElement = SelectorEngine.findOne(SELECTOR_INDICATORS, _this._element);
      _this._addEventListeners();
      if (_this._config.ride === CLASS_NAME_CAROUSEL) {
        _this.cycle();
      }
      return _this;
    }

    // Getters
    var _proto = Carousel.prototype;
    // Public
    _proto.next = function next() {
      this._slide(ORDER_NEXT);
    };
    _proto.nextWhenVisible = function nextWhenVisible() {
      // FIXME TODO use `document.visibilityState`
      // Don't call next when the page isn't visible
      // or the carousel or its parent isn't visible
      if (!document.hidden && isVisible(this._element)) {
        this.next();
      }
    };
    _proto.prev = function prev() {
      this._slide(ORDER_PREV);
    };
    _proto.pause = function pause() {
      if (this._isSliding) {
        triggerTransitionEnd(this._element);
      }
      this._clearInterval();
    };
    _proto.cycle = function cycle() {
      var _this2 = this;
      this._clearInterval();
      this._updateInterval();
      this._interval = setInterval(function () {
        return _this2.nextWhenVisible();
      }, this._config.interval);
    };
    _proto._maybeEnableCycle = function _maybeEnableCycle() {
      var _this3 = this;
      if (!this._config.ride) {
        return;
      }
      if (this._isSliding) {
        EventHandler.one(this._element, EVENT_SLID, function () {
          return _this3.cycle();
        });
        return;
      }
      this.cycle();
    };
    _proto.to = function to(index) {
      var _this4 = this;
      var items = this._getItems();
      if (index > items.length - 1 || index < 0) {
        return;
      }
      if (this._isSliding) {
        EventHandler.one(this._element, EVENT_SLID, function () {
          return _this4.to(index);
        });
        return;
      }
      var activeIndex = this._getItemIndex(this._getActive());
      if (activeIndex === index) {
        return;
      }
      var order = index > activeIndex ? ORDER_NEXT : ORDER_PREV;
      this._slide(order, items[index]);
    };
    _proto.dispose = function dispose() {
      if (this._swipeHelper) {
        this._swipeHelper.dispose();
      }
      _BaseComponent.prototype.dispose.call(this);
    }

    // Private
    ;
    _proto._configAfterMerge = function _configAfterMerge(config) {
      config.defaultInterval = config.interval;
      return config;
    };
    _proto._addEventListeners = function _addEventListeners() {
      var _this5 = this;
      if (this._config.keyboard) {
        EventHandler.on(this._element, EVENT_KEYDOWN$1, function (event) {
          return _this5._keydown(event);
        });
      }
      if (this._config.pause === 'hover') {
        EventHandler.on(this._element, EVENT_MOUSEENTER$1, function () {
          return _this5.pause();
        });
        EventHandler.on(this._element, EVENT_MOUSELEAVE$1, function () {
          return _this5._maybeEnableCycle();
        });
      }
      if (this._config.touch && Swipe.isSupported()) {
        this._addTouchEventListeners();
      }
    };
    _proto._addTouchEventListeners = function _addTouchEventListeners() {
      var _this6 = this;
      for (var _iterator = _createForOfIteratorHelperLoose(SelectorEngine.find(SELECTOR_ITEM_IMG, this._element)), _step; !(_step = _iterator()).done;) {
        var img = _step.value;
        EventHandler.on(img, EVENT_DRAG_START, function (event) {
          return event.preventDefault();
        });
      }
      var endCallBack = function endCallBack() {
        if (_this6._config.pause !== 'hover') {
          return;
        }

        // If it's a touch-enabled device, mouseenter/leave are fired as
        // part of the mouse compatibility events on first tap - the carousel
        // would stop cycling until user tapped out of it;
        // here, we listen for touchend, explicitly pause the carousel
        // (as if it's the second time we tap on it, mouseenter compat event
        // is NOT fired) and after a timeout (to allow for mouse compatibility
        // events to fire) we explicitly restart cycling

        _this6.pause();
        if (_this6.touchTimeout) {
          clearTimeout(_this6.touchTimeout);
        }
        _this6.touchTimeout = setTimeout(function () {
          return _this6._maybeEnableCycle();
        }, TOUCHEVENT_COMPAT_WAIT + _this6._config.interval);
      };
      var swipeConfig = {
        leftCallback: function leftCallback() {
          return _this6._slide(_this6._directionToOrder(DIRECTION_LEFT));
        },
        rightCallback: function rightCallback() {
          return _this6._slide(_this6._directionToOrder(DIRECTION_RIGHT));
        },
        endCallback: endCallBack
      };
      this._swipeHelper = new Swipe(this._element, swipeConfig);
    };
    _proto._keydown = function _keydown(event) {
      if (/input|textarea/i.test(event.target.tagName)) {
        return;
      }
      var direction = KEY_TO_DIRECTION[event.key];
      if (direction) {
        event.preventDefault();
        this._slide(this._directionToOrder(direction));
      }
    };
    _proto._getItemIndex = function _getItemIndex(element) {
      return this._getItems().indexOf(element);
    };
    _proto._setActiveIndicatorElement = function _setActiveIndicatorElement(index) {
      if (!this._indicatorsElement) {
        return;
      }
      var activeIndicator = SelectorEngine.findOne(SELECTOR_ACTIVE, this._indicatorsElement);
      activeIndicator.classList.remove(CLASS_NAME_ACTIVE$2);
      activeIndicator.removeAttribute('aria-current');
      var newActiveIndicator = SelectorEngine.findOne("[data-bs-slide-to=\"" + index + "\"]", this._indicatorsElement);
      if (newActiveIndicator) {
        newActiveIndicator.classList.add(CLASS_NAME_ACTIVE$2);
        newActiveIndicator.setAttribute('aria-current', 'true');
      }
    };
    _proto._updateInterval = function _updateInterval() {
      var element = this._activeElement || this._getActive();
      if (!element) {
        return;
      }
      var elementInterval = Number.parseInt(element.getAttribute('data-bs-interval'), 10);
      this._config.interval = elementInterval || this._config.defaultInterval;
    };
    _proto._slide = function _slide(order, element) {
      var _this7 = this;
      if (element === void 0) {
        element = null;
      }
      if (this._isSliding) {
        return;
      }
      var activeElement = this._getActive();
      var isNext = order === ORDER_NEXT;
      var nextElement = element || getNextActiveElement(this._getItems(), activeElement, isNext, this._config.wrap);
      if (nextElement === activeElement) {
        return;
      }
      var nextElementIndex = this._getItemIndex(nextElement);
      var triggerEvent = function triggerEvent(eventName) {
        return EventHandler.trigger(_this7._element, eventName, {
          relatedTarget: nextElement,
          direction: _this7._orderToDirection(order),
          from: _this7._getItemIndex(activeElement),
          to: nextElementIndex
        });
      };
      var slideEvent = triggerEvent(EVENT_SLIDE);
      if (slideEvent.defaultPrevented) {
        return;
      }
      if (!activeElement || !nextElement) {
        // Some weirdness is happening, so we bail
        // TODO: change tests that use empty divs to avoid this check
        return;
      }
      var isCycling = Boolean(this._interval);
      this.pause();
      this._isSliding = true;
      this._setActiveIndicatorElement(nextElementIndex);
      this._activeElement = nextElement;
      var directionalClassName = isNext ? CLASS_NAME_START : CLASS_NAME_END;
      var orderClassName = isNext ? CLASS_NAME_NEXT : CLASS_NAME_PREV;
      nextElement.classList.add(orderClassName);
      reflow(nextElement);
      activeElement.classList.add(directionalClassName);
      nextElement.classList.add(directionalClassName);
      var completeCallBack = function completeCallBack() {
        nextElement.classList.remove(directionalClassName, orderClassName);
        nextElement.classList.add(CLASS_NAME_ACTIVE$2);
        activeElement.classList.remove(CLASS_NAME_ACTIVE$2, orderClassName, directionalClassName);
        _this7._isSliding = false;
        triggerEvent(EVENT_SLID);
      };
      this._queueCallback(completeCallBack, activeElement, this._isAnimated());
      if (isCycling) {
        this.cycle();
      }
    };
    _proto._isAnimated = function _isAnimated() {
      return this._element.classList.contains(CLASS_NAME_SLIDE);
    };
    _proto._getActive = function _getActive() {
      return SelectorEngine.findOne(SELECTOR_ACTIVE_ITEM, this._element);
    };
    _proto._getItems = function _getItems() {
      return SelectorEngine.find(SELECTOR_ITEM, this._element);
    };
    _proto._clearInterval = function _clearInterval() {
      if (this._interval) {
        clearInterval(this._interval);
        this._interval = null;
      }
    };
    _proto._directionToOrder = function _directionToOrder(direction) {
      if (isRTL()) {
        return direction === DIRECTION_LEFT ? ORDER_PREV : ORDER_NEXT;
      }
      return direction === DIRECTION_LEFT ? ORDER_NEXT : ORDER_PREV;
    };
    _proto._orderToDirection = function _orderToDirection(order) {
      if (isRTL()) {
        return order === ORDER_PREV ? DIRECTION_LEFT : DIRECTION_RIGHT;
      }
      return order === ORDER_PREV ? DIRECTION_RIGHT : DIRECTION_LEFT;
    }

    // Static
    ;
    Carousel.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Carousel.getOrCreateInstance(this, config);
        if (typeof config === 'number') {
          data.to(config);
          return;
        }
        if (typeof config === 'string') {
          if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
            throw new TypeError("No method named \"" + config + "\"");
          }
          data[config]();
        }
      });
    };
    _createClass(Carousel, null, [{
      key: "Default",
      get: function get() {
        return Default$b;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$b;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$c;
      }
    }]);
    return Carousel;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API$5, SELECTOR_DATA_SLIDE, function (event) {
    var target = SelectorEngine.getElementFromSelector(this);
    if (!target || !target.classList.contains(CLASS_NAME_CAROUSEL)) {
      return;
    }
    event.preventDefault();
    var carousel = Carousel.getOrCreateInstance(target);
    var slideIndex = this.getAttribute('data-bs-slide-to');
    if (slideIndex) {
      carousel.to(slideIndex);
      carousel._maybeEnableCycle();
      return;
    }
    if (Manipulator.getDataAttribute(this, 'slide') === 'next') {
      carousel.next();
      carousel._maybeEnableCycle();
      return;
    }
    carousel.prev();
    carousel._maybeEnableCycle();
  });
  EventHandler.on(window, EVENT_LOAD_DATA_API$3, function () {
    var carousels = SelectorEngine.find(SELECTOR_DATA_RIDE);
    for (var _iterator2 = _createForOfIteratorHelperLoose(carousels), _step2; !(_step2 = _iterator2()).done;) {
      var carousel = _step2.value;
      Carousel.getOrCreateInstance(carousel);
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Carousel);

  /**
   * Constants
   */

  var NAME$b = 'collapse';
  var DATA_KEY$7 = 'bs.collapse';
  var EVENT_KEY$7 = "." + DATA_KEY$7;
  var DATA_API_KEY$4 = '.data-api';
  var EVENT_SHOW$6 = "show" + EVENT_KEY$7;
  var EVENT_SHOWN$6 = "shown" + EVENT_KEY$7;
  var EVENT_HIDE$6 = "hide" + EVENT_KEY$7;
  var EVENT_HIDDEN$6 = "hidden" + EVENT_KEY$7;
  var EVENT_CLICK_DATA_API$4 = "click" + EVENT_KEY$7 + DATA_API_KEY$4;
  var CLASS_NAME_SHOW$7 = 'show';
  var CLASS_NAME_COLLAPSE = 'collapse';
  var CLASS_NAME_COLLAPSING = 'collapsing';
  var CLASS_NAME_COLLAPSED = 'collapsed';
  var CLASS_NAME_DEEPER_CHILDREN = ":scope ." + CLASS_NAME_COLLAPSE + " ." + CLASS_NAME_COLLAPSE;
  var CLASS_NAME_HORIZONTAL = 'collapse-horizontal';
  var WIDTH = 'width';
  var HEIGHT = 'height';
  var SELECTOR_ACTIVES = '.collapse.show, .collapse.collapsing';
  var SELECTOR_DATA_TOGGLE$4 = '[data-bs-toggle="collapse"]';
  var Default$a = {
    parent: null,
    toggle: true
  };
  var DefaultType$a = {
    parent: '(null|element)',
    toggle: 'boolean'
  };

  /**
   * Class definition
   */
  var Collapse = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Collapse, _BaseComponent);
    function Collapse(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._isTransitioning = false;
      _this._triggerArray = [];
      var toggleList = SelectorEngine.find(SELECTOR_DATA_TOGGLE$4);
      for (var _iterator = _createForOfIteratorHelperLoose(toggleList), _step; !(_step = _iterator()).done;) {
        var elem = _step.value;
        var selector = SelectorEngine.getSelectorFromElement(elem);
        var filterElement = SelectorEngine.find(selector).filter(function (foundElement) {
          return foundElement === _this._element;
        });
        if (selector !== null && filterElement.length) {
          _this._triggerArray.push(elem);
        }
      }
      _this._initializeChildren();
      if (!_this._config.parent) {
        _this._addAriaAndCollapsedClass(_this._triggerArray, _this._isShown());
      }
      if (_this._config.toggle) {
        _this.toggle();
      }
      return _this;
    }

    // Getters
    var _proto = Collapse.prototype;
    // Public
    _proto.toggle = function toggle() {
      if (this._isShown()) {
        this.hide();
      } else {
        this.show();
      }
    };
    _proto.show = function show() {
      var _this2 = this;
      if (this._isTransitioning || this._isShown()) {
        return;
      }
      var activeChildren = [];

      // find active children
      if (this._config.parent) {
        activeChildren = this._getFirstLevelChildren(SELECTOR_ACTIVES).filter(function (element) {
          return element !== _this2._element;
        }).map(function (element) {
          return Collapse.getOrCreateInstance(element, {
            toggle: false
          });
        });
      }
      if (activeChildren.length && activeChildren[0]._isTransitioning) {
        return;
      }
      var startEvent = EventHandler.trigger(this._element, EVENT_SHOW$6);
      if (startEvent.defaultPrevented) {
        return;
      }
      for (var _iterator2 = _createForOfIteratorHelperLoose(activeChildren), _step2; !(_step2 = _iterator2()).done;) {
        var activeInstance = _step2.value;
        activeInstance.hide();
      }
      var dimension = this._getDimension();
      this._element.classList.remove(CLASS_NAME_COLLAPSE);
      this._element.classList.add(CLASS_NAME_COLLAPSING);
      this._element.style[dimension] = 0;
      this._addAriaAndCollapsedClass(this._triggerArray, true);
      this._isTransitioning = true;
      var complete = function complete() {
        _this2._isTransitioning = false;
        _this2._element.classList.remove(CLASS_NAME_COLLAPSING);
        _this2._element.classList.add(CLASS_NAME_COLLAPSE, CLASS_NAME_SHOW$7);
        _this2._element.style[dimension] = '';
        EventHandler.trigger(_this2._element, EVENT_SHOWN$6);
      };
      var capitalizedDimension = dimension[0].toUpperCase() + dimension.slice(1);
      var scrollSize = "scroll" + capitalizedDimension;
      this._queueCallback(complete, this._element, true);
      this._element.style[dimension] = this._element[scrollSize] + "px";
    };
    _proto.hide = function hide() {
      var _this3 = this;
      if (this._isTransitioning || !this._isShown()) {
        return;
      }
      var startEvent = EventHandler.trigger(this._element, EVENT_HIDE$6);
      if (startEvent.defaultPrevented) {
        return;
      }
      var dimension = this._getDimension();
      this._element.style[dimension] = this._element.getBoundingClientRect()[dimension] + "px";
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_COLLAPSING);
      this._element.classList.remove(CLASS_NAME_COLLAPSE, CLASS_NAME_SHOW$7);
      for (var _iterator3 = _createForOfIteratorHelperLoose(this._triggerArray), _step3; !(_step3 = _iterator3()).done;) {
        var trigger = _step3.value;
        var element = SelectorEngine.getElementFromSelector(trigger);
        if (element && !this._isShown(element)) {
          this._addAriaAndCollapsedClass([trigger], false);
        }
      }
      this._isTransitioning = true;
      var complete = function complete() {
        _this3._isTransitioning = false;
        _this3._element.classList.remove(CLASS_NAME_COLLAPSING);
        _this3._element.classList.add(CLASS_NAME_COLLAPSE);
        EventHandler.trigger(_this3._element, EVENT_HIDDEN$6);
      };
      this._element.style[dimension] = '';
      this._queueCallback(complete, this._element, true);
    }

    // Private
    ;
    _proto._isShown = function _isShown(element) {
      if (element === void 0) {
        element = this._element;
      }
      return element.classList.contains(CLASS_NAME_SHOW$7);
    };
    _proto._configAfterMerge = function _configAfterMerge(config) {
      config.toggle = Boolean(config.toggle); // Coerce string values
      config.parent = getElement(config.parent);
      return config;
    };
    _proto._getDimension = function _getDimension() {
      return this._element.classList.contains(CLASS_NAME_HORIZONTAL) ? WIDTH : HEIGHT;
    };
    _proto._initializeChildren = function _initializeChildren() {
      if (!this._config.parent) {
        return;
      }
      var children = this._getFirstLevelChildren(SELECTOR_DATA_TOGGLE$4);
      for (var _iterator4 = _createForOfIteratorHelperLoose(children), _step4; !(_step4 = _iterator4()).done;) {
        var element = _step4.value;
        var selected = SelectorEngine.getElementFromSelector(element);
        if (selected) {
          this._addAriaAndCollapsedClass([element], this._isShown(selected));
        }
      }
    };
    _proto._getFirstLevelChildren = function _getFirstLevelChildren(selector) {
      var children = SelectorEngine.find(CLASS_NAME_DEEPER_CHILDREN, this._config.parent);
      // remove children if greater depth
      return SelectorEngine.find(selector, this._config.parent).filter(function (element) {
        return !children.includes(element);
      });
    };
    _proto._addAriaAndCollapsedClass = function _addAriaAndCollapsedClass(triggerArray, isOpen) {
      if (!triggerArray.length) {
        return;
      }
      for (var _iterator5 = _createForOfIteratorHelperLoose(triggerArray), _step5; !(_step5 = _iterator5()).done;) {
        var element = _step5.value;
        element.classList.toggle(CLASS_NAME_COLLAPSED, !isOpen);
        element.setAttribute('aria-expanded', isOpen);
      }
    }

    // Static
    ;
    Collapse.jQueryInterface = function jQueryInterface(config) {
      var _config = {};
      if (typeof config === 'string' && /show|hide/.test(config)) {
        _config.toggle = false;
      }
      return this.each(function () {
        var data = Collapse.getOrCreateInstance(this, _config);
        if (typeof config === 'string') {
          if (typeof data[config] === 'undefined') {
            throw new TypeError("No method named \"" + config + "\"");
          }
          data[config]();
        }
      });
    };
    _createClass(Collapse, null, [{
      key: "Default",
      get: function get() {
        return Default$a;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$a;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$b;
      }
    }]);
    return Collapse;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API$4, SELECTOR_DATA_TOGGLE$4, function (event) {
    // preventDefault only for <a> elements (which change the URL) not inside the collapsible element
    if (event.target.tagName === 'A' || event.delegateTarget && event.delegateTarget.tagName === 'A') {
      event.preventDefault();
    }
    for (var _iterator6 = _createForOfIteratorHelperLoose(SelectorEngine.getMultipleElementsFromSelector(this)), _step6; !(_step6 = _iterator6()).done;) {
      var element = _step6.value;
      Collapse.getOrCreateInstance(element, {
        toggle: false
      }).toggle();
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Collapse);

  /**
   * Constants
   */

  var NAME$a = 'dropdown';
  var DATA_KEY$6 = 'bs.dropdown';
  var EVENT_KEY$6 = "." + DATA_KEY$6;
  var DATA_API_KEY$3 = '.data-api';
  var ESCAPE_KEY$2 = 'Escape';
  var TAB_KEY$1 = 'Tab';
  var ARROW_UP_KEY$1 = 'ArrowUp';
  var ARROW_DOWN_KEY$1 = 'ArrowDown';
  var RIGHT_MOUSE_BUTTON = 2; // MouseEvent.button value for the secondary button, usually the right button

  var EVENT_HIDE$5 = "hide" + EVENT_KEY$6;
  var EVENT_HIDDEN$5 = "hidden" + EVENT_KEY$6;
  var EVENT_SHOW$5 = "show" + EVENT_KEY$6;
  var EVENT_SHOWN$5 = "shown" + EVENT_KEY$6;
  var EVENT_CLICK_DATA_API$3 = "click" + EVENT_KEY$6 + DATA_API_KEY$3;
  var EVENT_KEYDOWN_DATA_API = "keydown" + EVENT_KEY$6 + DATA_API_KEY$3;
  var EVENT_KEYUP_DATA_API = "keyup" + EVENT_KEY$6 + DATA_API_KEY$3;
  var CLASS_NAME_SHOW$6 = 'show';
  var CLASS_NAME_DROPUP = 'dropup';
  var CLASS_NAME_DROPEND = 'dropend';
  var CLASS_NAME_DROPSTART = 'dropstart';
  var CLASS_NAME_DROPUP_CENTER = 'dropup-center';
  var CLASS_NAME_DROPDOWN_CENTER = 'dropdown-center';
  var SELECTOR_DATA_TOGGLE$3 = '[data-bs-toggle="dropdown"]:not(.disabled):not(:disabled)';
  var SELECTOR_DATA_TOGGLE_SHOWN = SELECTOR_DATA_TOGGLE$3 + "." + CLASS_NAME_SHOW$6;
  var SELECTOR_MENU = '.dropdown-menu';
  var SELECTOR_NAVBAR = '.navbar';
  var SELECTOR_NAVBAR_NAV = '.navbar-nav';
  var SELECTOR_VISIBLE_ITEMS = '.dropdown-menu .dropdown-item:not(.disabled):not(:disabled)';
  var PLACEMENT_TOP = isRTL() ? 'top-end' : 'top-start';
  var PLACEMENT_TOPEND = isRTL() ? 'top-start' : 'top-end';
  var PLACEMENT_BOTTOM = isRTL() ? 'bottom-end' : 'bottom-start';
  var PLACEMENT_BOTTOMEND = isRTL() ? 'bottom-start' : 'bottom-end';
  var PLACEMENT_RIGHT = isRTL() ? 'left-start' : 'right-start';
  var PLACEMENT_LEFT = isRTL() ? 'right-start' : 'left-start';
  var PLACEMENT_TOPCENTER = 'top';
  var PLACEMENT_BOTTOMCENTER = 'bottom';
  var Default$9 = {
    autoClose: true,
    boundary: 'clippingParents',
    display: 'dynamic',
    offset: [0, 2],
    popperConfig: null,
    reference: 'toggle'
  };
  var DefaultType$9 = {
    autoClose: '(boolean|string)',
    boundary: '(string|element)',
    display: 'string',
    offset: '(array|string|function)',
    popperConfig: '(null|object|function)',
    reference: '(string|element|object)'
  };

  /**
   * Class definition
   */
  var Dropdown = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Dropdown, _BaseComponent);
    function Dropdown(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._popper = null;
      _this._parent = _this._element.parentNode; // dropdown wrapper
      // TODO: v6 revert #37011 & change markup https://getbootstrap.com/docs/5.3/forms/input-group/
      _this._menu = SelectorEngine.next(_this._element, SELECTOR_MENU)[0] || SelectorEngine.prev(_this._element, SELECTOR_MENU)[0] || SelectorEngine.findOne(SELECTOR_MENU, _this._parent);
      _this._inNavbar = _this._detectNavbar();
      return _this;
    }

    // Getters
    var _proto = Dropdown.prototype;
    // Public
    _proto.toggle = function toggle() {
      return this._isShown() ? this.hide() : this.show();
    };
    _proto.show = function show() {
      if (isDisabled(this._element) || this._isShown()) {
        return;
      }
      var relatedTarget = {
        relatedTarget: this._element
      };
      var showEvent = EventHandler.trigger(this._element, EVENT_SHOW$5, relatedTarget);
      if (showEvent.defaultPrevented) {
        return;
      }
      this._createPopper();

      // If this is a touch-enabled device we add extra
      // empty mouseover listeners to the body's immediate children;
      // only needed because of broken event delegation on iOS
      // https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html
      if ('ontouchstart' in document.documentElement && !this._parent.closest(SELECTOR_NAVBAR_NAV)) {
        for (var _iterator = _createForOfIteratorHelperLoose((_ref = []).concat.apply(_ref, document.body.children)), _step; !(_step = _iterator()).done;) {
          var _ref;
          var element = _step.value;
          EventHandler.on(element, 'mouseover', noop);
        }
      }
      this._element.focus();
      this._element.setAttribute('aria-expanded', true);
      this._menu.classList.add(CLASS_NAME_SHOW$6);
      this._element.classList.add(CLASS_NAME_SHOW$6);
      EventHandler.trigger(this._element, EVENT_SHOWN$5, relatedTarget);
    };
    _proto.hide = function hide() {
      if (isDisabled(this._element) || !this._isShown()) {
        return;
      }
      var relatedTarget = {
        relatedTarget: this._element
      };
      this._completeHide(relatedTarget);
    };
    _proto.dispose = function dispose() {
      if (this._popper) {
        this._popper.destroy();
      }
      _BaseComponent.prototype.dispose.call(this);
    };
    _proto.update = function update() {
      this._inNavbar = this._detectNavbar();
      if (this._popper) {
        this._popper.update();
      }
    }

    // Private
    ;
    _proto._completeHide = function _completeHide(relatedTarget) {
      var hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$5, relatedTarget);
      if (hideEvent.defaultPrevented) {
        return;
      }

      // If this is a touch-enabled device we remove the extra
      // empty mouseover listeners we added for iOS support
      if ('ontouchstart' in document.documentElement) {
        for (var _iterator2 = _createForOfIteratorHelperLoose((_ref2 = []).concat.apply(_ref2, document.body.children)), _step2; !(_step2 = _iterator2()).done;) {
          var _ref2;
          var element = _step2.value;
          EventHandler.off(element, 'mouseover', noop);
        }
      }
      if (this._popper) {
        this._popper.destroy();
      }
      this._menu.classList.remove(CLASS_NAME_SHOW$6);
      this._element.classList.remove(CLASS_NAME_SHOW$6);
      this._element.setAttribute('aria-expanded', 'false');
      Manipulator.removeDataAttribute(this._menu, 'popper');
      EventHandler.trigger(this._element, EVENT_HIDDEN$5, relatedTarget);
    };
    _proto._getConfig = function _getConfig(config) {
      config = _BaseComponent.prototype._getConfig.call(this, config);
      if (typeof config.reference === 'object' && !isElement(config.reference) && typeof config.reference.getBoundingClientRect !== 'function') {
        // Popper virtual elements require a getBoundingClientRect method
        throw new TypeError(NAME$a.toUpperCase() + ": Option \"reference\" provided type \"object\" without a required \"getBoundingClientRect\" method.");
      }
      return config;
    };
    _proto._createPopper = function _createPopper() {
      if (typeof Popper__namespace === 'undefined') {
        throw new TypeError('Bootstrap\'s dropdowns require Popper (https://popper.js.org/docs/v2/)');
      }
      var referenceElement = this._element;
      if (this._config.reference === 'parent') {
        referenceElement = this._parent;
      } else if (isElement(this._config.reference)) {
        referenceElement = getElement(this._config.reference);
      } else if (typeof this._config.reference === 'object') {
        referenceElement = this._config.reference;
      }
      var popperConfig = this._getPopperConfig();
      this._popper = Popper__namespace.createPopper(referenceElement, this._menu, popperConfig);
    };
    _proto._isShown = function _isShown() {
      return this._menu.classList.contains(CLASS_NAME_SHOW$6);
    };
    _proto._getPlacement = function _getPlacement() {
      var parentDropdown = this._parent;
      if (parentDropdown.classList.contains(CLASS_NAME_DROPEND)) {
        return PLACEMENT_RIGHT;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPSTART)) {
        return PLACEMENT_LEFT;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPUP_CENTER)) {
        return PLACEMENT_TOPCENTER;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPDOWN_CENTER)) {
        return PLACEMENT_BOTTOMCENTER;
      }

      // We need to trim the value because custom properties can also include spaces
      var isEnd = getComputedStyle(this._menu).getPropertyValue('--bs-position').trim() === 'end';
      if (parentDropdown.classList.contains(CLASS_NAME_DROPUP)) {
        return isEnd ? PLACEMENT_TOPEND : PLACEMENT_TOP;
      }
      return isEnd ? PLACEMENT_BOTTOMEND : PLACEMENT_BOTTOM;
    };
    _proto._detectNavbar = function _detectNavbar() {
      return this._element.closest(SELECTOR_NAVBAR) !== null;
    };
    _proto._getOffset = function _getOffset() {
      var _this2 = this;
      var offset = this._config.offset;
      if (typeof offset === 'string') {
        return offset.split(',').map(function (value) {
          return Number.parseInt(value, 10);
        });
      }
      if (typeof offset === 'function') {
        return function (popperData) {
          return offset(popperData, _this2._element);
        };
      }
      return offset;
    };
    _proto._getPopperConfig = function _getPopperConfig() {
      var defaultBsPopperConfig = {
        placement: this._getPlacement(),
        modifiers: [{
          name: 'preventOverflow',
          options: {
            boundary: this._config.boundary
          }
        }, {
          name: 'offset',
          options: {
            offset: this._getOffset()
          }
        }]
      };

      // Disable Popper if we have a static display or Dropdown is in Navbar
      if (this._inNavbar || this._config.display === 'static') {
        Manipulator.setDataAttribute(this._menu, 'popper', 'static'); // TODO: v6 remove
        defaultBsPopperConfig.modifiers = [{
          name: 'applyStyles',
          enabled: false
        }];
      }
      return _extends({}, defaultBsPopperConfig, execute(this._config.popperConfig, [undefined, defaultBsPopperConfig]));
    };
    _proto._selectMenuItem = function _selectMenuItem(_ref3) {
      var key = _ref3.key,
        target = _ref3.target;
      var items = SelectorEngine.find(SELECTOR_VISIBLE_ITEMS, this._menu).filter(function (element) {
        return isVisible(element);
      });
      if (!items.length) {
        return;
      }

      // if target isn't included in items (e.g. when expanding the dropdown)
      // allow cycling to get the last item in case key equals ARROW_UP_KEY
      getNextActiveElement(items, target, key === ARROW_DOWN_KEY$1, !items.includes(target)).focus();
    }

    // Static
    ;
    Dropdown.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Dropdown.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config]();
      });
    };
    Dropdown.clearMenus = function clearMenus(event) {
      if (event.button === RIGHT_MOUSE_BUTTON || event.type === 'keyup' && event.key !== TAB_KEY$1) {
        return;
      }
      var openToggles = SelectorEngine.find(SELECTOR_DATA_TOGGLE_SHOWN);
      for (var _iterator3 = _createForOfIteratorHelperLoose(openToggles), _step3; !(_step3 = _iterator3()).done;) {
        var toggle = _step3.value;
        var context = Dropdown.getInstance(toggle);
        if (!context || context._config.autoClose === false) {
          continue;
        }
        var composedPath = event.composedPath();
        var isMenuTarget = composedPath.includes(context._menu);
        if (composedPath.includes(context._element) || context._config.autoClose === 'inside' && !isMenuTarget || context._config.autoClose === 'outside' && isMenuTarget) {
          continue;
        }

        // Tab navigation through the dropdown menu or events from contained inputs shouldn't close the menu
        if (context._menu.contains(event.target) && (event.type === 'keyup' && event.key === TAB_KEY$1 || /input|select|option|textarea|form/i.test(event.target.tagName))) {
          continue;
        }
        var relatedTarget = {
          relatedTarget: context._element
        };
        if (event.type === 'click') {
          relatedTarget.clickEvent = event;
        }
        context._completeHide(relatedTarget);
      }
    };
    Dropdown.dataApiKeydownHandler = function dataApiKeydownHandler(event) {
      // If not an UP | DOWN | ESCAPE key => not a dropdown command
      // If input/textarea && if key is other than ESCAPE => not a dropdown command

      var isInput = /input|textarea/i.test(event.target.tagName);
      var isEscapeEvent = event.key === ESCAPE_KEY$2;
      var isUpOrDownEvent = [ARROW_UP_KEY$1, ARROW_DOWN_KEY$1].includes(event.key);
      if (!isUpOrDownEvent && !isEscapeEvent) {
        return;
      }
      if (isInput && !isEscapeEvent) {
        return;
      }
      event.preventDefault();

      // TODO: v6 revert #37011 & change markup https://getbootstrap.com/docs/5.3/forms/input-group/
      var getToggleButton = this.matches(SELECTOR_DATA_TOGGLE$3) ? this : SelectorEngine.prev(this, SELECTOR_DATA_TOGGLE$3)[0] || SelectorEngine.next(this, SELECTOR_DATA_TOGGLE$3)[0] || SelectorEngine.findOne(SELECTOR_DATA_TOGGLE$3, event.delegateTarget.parentNode);
      var instance = Dropdown.getOrCreateInstance(getToggleButton);
      if (isUpOrDownEvent) {
        event.stopPropagation();
        instance.show();
        instance._selectMenuItem(event);
        return;
      }
      if (instance._isShown()) {
        // else is escape and we check if it is shown
        event.stopPropagation();
        instance.hide();
        getToggleButton.focus();
      }
    };
    _createClass(Dropdown, null, [{
      key: "Default",
      get: function get() {
        return Default$9;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$9;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$a;
      }
    }]);
    return Dropdown;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_KEYDOWN_DATA_API, SELECTOR_DATA_TOGGLE$3, Dropdown.dataApiKeydownHandler);
  EventHandler.on(document, EVENT_KEYDOWN_DATA_API, SELECTOR_MENU, Dropdown.dataApiKeydownHandler);
  EventHandler.on(document, EVENT_CLICK_DATA_API$3, Dropdown.clearMenus);
  EventHandler.on(document, EVENT_KEYUP_DATA_API, Dropdown.clearMenus);
  EventHandler.on(document, EVENT_CLICK_DATA_API$3, SELECTOR_DATA_TOGGLE$3, function (event) {
    event.preventDefault();
    Dropdown.getOrCreateInstance(this).toggle();
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Dropdown);

  /**
   * Constants
   */

  var NAME$9 = 'backdrop';
  var CLASS_NAME_FADE$4 = 'fade';
  var CLASS_NAME_SHOW$5 = 'show';
  var EVENT_MOUSEDOWN = "mousedown.bs." + NAME$9;
  var Default$8 = {
    className: 'modal-backdrop',
    clickCallback: null,
    isAnimated: false,
    isVisible: true,
    // if false, we use the backdrop helper without adding any element to the dom
    rootElement: 'body' // give the choice to place backdrop under different elements
  };

  var DefaultType$8 = {
    className: 'string',
    clickCallback: '(function|null)',
    isAnimated: 'boolean',
    isVisible: 'boolean',
    rootElement: '(element|string)'
  };

  /**
   * Class definition
   */
  var Backdrop = /*#__PURE__*/function (_Config) {
    _inheritsLoose(Backdrop, _Config);
    function Backdrop(config) {
      var _this;
      _this = _Config.call(this) || this;
      _this._config = _this._getConfig(config);
      _this._isAppended = false;
      _this._element = null;
      return _this;
    }

    // Getters
    var _proto = Backdrop.prototype;
    // Public
    _proto.show = function show(callback) {
      if (!this._config.isVisible) {
        execute(callback);
        return;
      }
      this._append();
      var element = this._getElement();
      if (this._config.isAnimated) {
        reflow(element);
      }
      element.classList.add(CLASS_NAME_SHOW$5);
      this._emulateAnimation(function () {
        execute(callback);
      });
    };
    _proto.hide = function hide(callback) {
      var _this2 = this;
      if (!this._config.isVisible) {
        execute(callback);
        return;
      }
      this._getElement().classList.remove(CLASS_NAME_SHOW$5);
      this._emulateAnimation(function () {
        _this2.dispose();
        execute(callback);
      });
    };
    _proto.dispose = function dispose() {
      if (!this._isAppended) {
        return;
      }
      EventHandler.off(this._element, EVENT_MOUSEDOWN);
      this._element.remove();
      this._isAppended = false;
    }

    // Private
    ;
    _proto._getElement = function _getElement() {
      if (!this._element) {
        var backdrop = document.createElement('div');
        backdrop.className = this._config.className;
        if (this._config.isAnimated) {
          backdrop.classList.add(CLASS_NAME_FADE$4);
        }
        this._element = backdrop;
      }
      return this._element;
    };
    _proto._configAfterMerge = function _configAfterMerge(config) {
      // use getElement() with the default "body" to get a fresh Element on each instantiation
      config.rootElement = getElement(config.rootElement);
      return config;
    };
    _proto._append = function _append() {
      var _this3 = this;
      if (this._isAppended) {
        return;
      }
      var element = this._getElement();
      this._config.rootElement.append(element);
      EventHandler.on(element, EVENT_MOUSEDOWN, function () {
        execute(_this3._config.clickCallback);
      });
      this._isAppended = true;
    };
    _proto._emulateAnimation = function _emulateAnimation(callback) {
      executeAfterTransition(callback, this._getElement(), this._config.isAnimated);
    };
    _createClass(Backdrop, null, [{
      key: "Default",
      get: function get() {
        return Default$8;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$8;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$9;
      }
    }]);
    return Backdrop;
  }(Config);

  /**
   * Constants
   */

  var NAME$8 = 'focustrap';
  var DATA_KEY$5 = 'bs.focustrap';
  var EVENT_KEY$5 = "." + DATA_KEY$5;
  var EVENT_FOCUSIN$2 = "focusin" + EVENT_KEY$5;
  var EVENT_KEYDOWN_TAB = "keydown.tab" + EVENT_KEY$5;
  var TAB_KEY = 'Tab';
  var TAB_NAV_FORWARD = 'forward';
  var TAB_NAV_BACKWARD = 'backward';
  var Default$7 = {
    autofocus: true,
    trapElement: null // The element to trap focus inside of
  };

  var DefaultType$7 = {
    autofocus: 'boolean',
    trapElement: 'element'
  };

  /**
   * Class definition
   */
  var FocusTrap = /*#__PURE__*/function (_Config) {
    _inheritsLoose(FocusTrap, _Config);
    function FocusTrap(config) {
      var _this;
      _this = _Config.call(this) || this;
      _this._config = _this._getConfig(config);
      _this._isActive = false;
      _this._lastTabNavDirection = null;
      return _this;
    }

    // Getters
    var _proto = FocusTrap.prototype;
    // Public
    _proto.activate = function activate() {
      var _this2 = this;
      if (this._isActive) {
        return;
      }
      if (this._config.autofocus) {
        this._config.trapElement.focus();
      }
      EventHandler.off(document, EVENT_KEY$5); // guard against infinite focus loop
      EventHandler.on(document, EVENT_FOCUSIN$2, function (event) {
        return _this2._handleFocusin(event);
      });
      EventHandler.on(document, EVENT_KEYDOWN_TAB, function (event) {
        return _this2._handleKeydown(event);
      });
      this._isActive = true;
    };
    _proto.deactivate = function deactivate() {
      if (!this._isActive) {
        return;
      }
      this._isActive = false;
      EventHandler.off(document, EVENT_KEY$5);
    }

    // Private
    ;
    _proto._handleFocusin = function _handleFocusin(event) {
      var trapElement = this._config.trapElement;
      if (event.target === document || event.target === trapElement || trapElement.contains(event.target)) {
        return;
      }
      var elements = SelectorEngine.focusableChildren(trapElement);
      if (elements.length === 0) {
        trapElement.focus();
      } else if (this._lastTabNavDirection === TAB_NAV_BACKWARD) {
        elements[elements.length - 1].focus();
      } else {
        elements[0].focus();
      }
    };
    _proto._handleKeydown = function _handleKeydown(event) {
      if (event.key !== TAB_KEY) {
        return;
      }
      this._lastTabNavDirection = event.shiftKey ? TAB_NAV_BACKWARD : TAB_NAV_FORWARD;
    };
    _createClass(FocusTrap, null, [{
      key: "Default",
      get: function get() {
        return Default$7;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$7;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$8;
      }
    }]);
    return FocusTrap;
  }(Config);

  /**
   * Constants
   */

  var SELECTOR_FIXED_CONTENT = '.fixed-top, .fixed-bottom, .is-fixed, .sticky-top';
  var SELECTOR_STICKY_CONTENT = '.sticky-top';
  var PROPERTY_PADDING = 'padding-right';
  var PROPERTY_MARGIN = 'margin-right';

  /**
   * Class definition
   */
  var ScrollBarHelper = /*#__PURE__*/function () {
    function ScrollBarHelper() {
      this._element = document.body;
    }

    // Public
    var _proto = ScrollBarHelper.prototype;
    _proto.getWidth = function getWidth() {
      // https://developer.mozilla.org/en-US/docs/Web/API/Window/innerWidth#usage_notes
      var documentWidth = document.documentElement.clientWidth;
      return Math.abs(window.innerWidth - documentWidth);
    };
    _proto.hide = function hide() {
      var width = this.getWidth();
      this._disableOverFlow();
      // give padding to element to balance the hidden scrollbar width
      this._setElementAttributes(this._element, PROPERTY_PADDING, function (calculatedValue) {
        return calculatedValue + width;
      });
      // trick: We adjust positive paddingRight and negative marginRight to sticky-top elements to keep showing fullwidth
      this._setElementAttributes(SELECTOR_FIXED_CONTENT, PROPERTY_PADDING, function (calculatedValue) {
        return calculatedValue + width;
      });
      this._setElementAttributes(SELECTOR_STICKY_CONTENT, PROPERTY_MARGIN, function (calculatedValue) {
        return calculatedValue - width;
      });
    };
    _proto.reset = function reset() {
      this._resetElementAttributes(this._element, 'overflow');
      this._resetElementAttributes(this._element, PROPERTY_PADDING);
      this._resetElementAttributes(SELECTOR_FIXED_CONTENT, PROPERTY_PADDING);
      this._resetElementAttributes(SELECTOR_STICKY_CONTENT, PROPERTY_MARGIN);
    };
    _proto.isOverflowing = function isOverflowing() {
      return this.getWidth() > 0;
    }

    // Private
    ;
    _proto._disableOverFlow = function _disableOverFlow() {
      this._saveInitialAttribute(this._element, 'overflow');
      this._element.style.overflow = 'hidden';
    };
    _proto._setElementAttributes = function _setElementAttributes(selector, styleProperty, callback) {
      var _this = this;
      var scrollbarWidth = this.getWidth();
      var manipulationCallBack = function manipulationCallBack(element) {
        if (element !== _this._element && window.innerWidth > element.clientWidth + scrollbarWidth) {
          return;
        }
        _this._saveInitialAttribute(element, styleProperty);
        var calculatedValue = window.getComputedStyle(element).getPropertyValue(styleProperty);
        element.style.setProperty(styleProperty, callback(Number.parseFloat(calculatedValue)) + "px");
      };
      this._applyManipulationCallback(selector, manipulationCallBack);
    };
    _proto._saveInitialAttribute = function _saveInitialAttribute(element, styleProperty) {
      var actualValue = element.style.getPropertyValue(styleProperty);
      if (actualValue) {
        Manipulator.setDataAttribute(element, styleProperty, actualValue);
      }
    };
    _proto._resetElementAttributes = function _resetElementAttributes(selector, styleProperty) {
      var manipulationCallBack = function manipulationCallBack(element) {
        var value = Manipulator.getDataAttribute(element, styleProperty);
        // We only want to remove the property if the value is `null`; the value can also be zero
        if (value === null) {
          element.style.removeProperty(styleProperty);
          return;
        }
        Manipulator.removeDataAttribute(element, styleProperty);
        element.style.setProperty(styleProperty, value);
      };
      this._applyManipulationCallback(selector, manipulationCallBack);
    };
    _proto._applyManipulationCallback = function _applyManipulationCallback(selector, callBack) {
      if (isElement(selector)) {
        callBack(selector);
        return;
      }
      for (var _iterator = _createForOfIteratorHelperLoose(SelectorEngine.find(selector, this._element)), _step; !(_step = _iterator()).done;) {
        var sel = _step.value;
        callBack(sel);
      }
    };
    return ScrollBarHelper;
  }();

  /**
   * Constants
   */

  var NAME$7 = 'modal';
  var DATA_KEY$4 = 'bs.modal';
  var EVENT_KEY$4 = "." + DATA_KEY$4;
  var DATA_API_KEY$2 = '.data-api';
  var ESCAPE_KEY$1 = 'Escape';
  var EVENT_HIDE$4 = "hide" + EVENT_KEY$4;
  var EVENT_HIDE_PREVENTED$1 = "hidePrevented" + EVENT_KEY$4;
  var EVENT_HIDDEN$4 = "hidden" + EVENT_KEY$4;
  var EVENT_SHOW$4 = "show" + EVENT_KEY$4;
  var EVENT_SHOWN$4 = "shown" + EVENT_KEY$4;
  var EVENT_RESIZE$1 = "resize" + EVENT_KEY$4;
  var EVENT_CLICK_DISMISS = "click.dismiss" + EVENT_KEY$4;
  var EVENT_MOUSEDOWN_DISMISS = "mousedown.dismiss" + EVENT_KEY$4;
  var EVENT_KEYDOWN_DISMISS$1 = "keydown.dismiss" + EVENT_KEY$4;
  var EVENT_CLICK_DATA_API$2 = "click" + EVENT_KEY$4 + DATA_API_KEY$2;
  var CLASS_NAME_OPEN = 'modal-open';
  var CLASS_NAME_FADE$3 = 'fade';
  var CLASS_NAME_SHOW$4 = 'show';
  var CLASS_NAME_STATIC = 'modal-static';
  var OPEN_SELECTOR$1 = '.modal.show';
  var SELECTOR_DIALOG = '.modal-dialog';
  var SELECTOR_MODAL_BODY = '.modal-body';
  var SELECTOR_DATA_TOGGLE$2 = '[data-bs-toggle="modal"]';
  var Default$6 = {
    backdrop: true,
    focus: true,
    keyboard: true
  };
  var DefaultType$6 = {
    backdrop: '(boolean|string)',
    focus: 'boolean',
    keyboard: 'boolean'
  };

  /**
   * Class definition
   */
  var Modal = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Modal, _BaseComponent);
    function Modal(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._dialog = SelectorEngine.findOne(SELECTOR_DIALOG, _this._element);
      _this._backdrop = _this._initializeBackDrop();
      _this._focustrap = _this._initializeFocusTrap();
      _this._isShown = false;
      _this._isTransitioning = false;
      _this._scrollBar = new ScrollBarHelper();
      _this._addEventListeners();
      return _this;
    }

    // Getters
    var _proto = Modal.prototype;
    // Public
    _proto.toggle = function toggle(relatedTarget) {
      return this._isShown ? this.hide() : this.show(relatedTarget);
    };
    _proto.show = function show(relatedTarget) {
      var _this2 = this;
      if (this._isShown || this._isTransitioning) {
        return;
      }
      var showEvent = EventHandler.trigger(this._element, EVENT_SHOW$4, {
        relatedTarget: relatedTarget
      });
      if (showEvent.defaultPrevented) {
        return;
      }
      this._isShown = true;
      this._isTransitioning = true;
      this._scrollBar.hide();
      document.body.classList.add(CLASS_NAME_OPEN);
      this._adjustDialog();
      this._backdrop.show(function () {
        return _this2._showElement(relatedTarget);
      });
    };
    _proto.hide = function hide() {
      var _this3 = this;
      if (!this._isShown || this._isTransitioning) {
        return;
      }
      var hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$4);
      if (hideEvent.defaultPrevented) {
        return;
      }
      this._isShown = false;
      this._isTransitioning = true;
      this._focustrap.deactivate();
      this._element.classList.remove(CLASS_NAME_SHOW$4);
      this._queueCallback(function () {
        return _this3._hideModal();
      }, this._element, this._isAnimated());
    };
    _proto.dispose = function dispose() {
      EventHandler.off(window, EVENT_KEY$4);
      EventHandler.off(this._dialog, EVENT_KEY$4);
      this._backdrop.dispose();
      this._focustrap.deactivate();
      _BaseComponent.prototype.dispose.call(this);
    };
    _proto.handleUpdate = function handleUpdate() {
      this._adjustDialog();
    }

    // Private
    ;
    _proto._initializeBackDrop = function _initializeBackDrop() {
      return new Backdrop({
        isVisible: Boolean(this._config.backdrop),
        // 'static' option will be translated to true, and booleans will keep their value,
        isAnimated: this._isAnimated()
      });
    };
    _proto._initializeFocusTrap = function _initializeFocusTrap() {
      return new FocusTrap({
        trapElement: this._element
      });
    };
    _proto._showElement = function _showElement(relatedTarget) {
      var _this4 = this;
      // try to append dynamic modal
      if (!document.body.contains(this._element)) {
        document.body.append(this._element);
      }
      this._element.style.display = 'block';
      this._element.removeAttribute('aria-hidden');
      this._element.setAttribute('aria-modal', true);
      this._element.setAttribute('role', 'dialog');
      this._element.scrollTop = 0;
      var modalBody = SelectorEngine.findOne(SELECTOR_MODAL_BODY, this._dialog);
      if (modalBody) {
        modalBody.scrollTop = 0;
      }
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_SHOW$4);
      var transitionComplete = function transitionComplete() {
        if (_this4._config.focus) {
          _this4._focustrap.activate();
        }
        _this4._isTransitioning = false;
        EventHandler.trigger(_this4._element, EVENT_SHOWN$4, {
          relatedTarget: relatedTarget
        });
      };
      this._queueCallback(transitionComplete, this._dialog, this._isAnimated());
    };
    _proto._addEventListeners = function _addEventListeners() {
      var _this5 = this;
      EventHandler.on(this._element, EVENT_KEYDOWN_DISMISS$1, function (event) {
        if (event.key !== ESCAPE_KEY$1) {
          return;
        }
        if (_this5._config.keyboard) {
          _this5.hide();
          return;
        }
        _this5._triggerBackdropTransition();
      });
      EventHandler.on(window, EVENT_RESIZE$1, function () {
        if (_this5._isShown && !_this5._isTransitioning) {
          _this5._adjustDialog();
        }
      });
      EventHandler.on(this._element, EVENT_MOUSEDOWN_DISMISS, function (event) {
        // a bad trick to segregate clicks that may start inside dialog but end outside, and avoid listen to scrollbar clicks
        EventHandler.one(_this5._element, EVENT_CLICK_DISMISS, function (event2) {
          if (_this5._element !== event.target || _this5._element !== event2.target) {
            return;
          }
          if (_this5._config.backdrop === 'static') {
            _this5._triggerBackdropTransition();
            return;
          }
          if (_this5._config.backdrop) {
            _this5.hide();
          }
        });
      });
    };
    _proto._hideModal = function _hideModal() {
      var _this6 = this;
      this._element.style.display = 'none';
      this._element.setAttribute('aria-hidden', true);
      this._element.removeAttribute('aria-modal');
      this._element.removeAttribute('role');
      this._isTransitioning = false;
      this._backdrop.hide(function () {
        document.body.classList.remove(CLASS_NAME_OPEN);
        _this6._resetAdjustments();
        _this6._scrollBar.reset();
        EventHandler.trigger(_this6._element, EVENT_HIDDEN$4);
      });
    };
    _proto._isAnimated = function _isAnimated() {
      return this._element.classList.contains(CLASS_NAME_FADE$3);
    };
    _proto._triggerBackdropTransition = function _triggerBackdropTransition() {
      var _this7 = this;
      var hideEvent = EventHandler.trigger(this._element, EVENT_HIDE_PREVENTED$1);
      if (hideEvent.defaultPrevented) {
        return;
      }
      var isModalOverflowing = this._element.scrollHeight > document.documentElement.clientHeight;
      var initialOverflowY = this._element.style.overflowY;
      // return if the following background transition hasn't yet completed
      if (initialOverflowY === 'hidden' || this._element.classList.contains(CLASS_NAME_STATIC)) {
        return;
      }
      if (!isModalOverflowing) {
        this._element.style.overflowY = 'hidden';
      }
      this._element.classList.add(CLASS_NAME_STATIC);
      this._queueCallback(function () {
        _this7._element.classList.remove(CLASS_NAME_STATIC);
        _this7._queueCallback(function () {
          _this7._element.style.overflowY = initialOverflowY;
        }, _this7._dialog);
      }, this._dialog);
      this._element.focus();
    }

    /**
     * The following methods are used to handle overflowing modals
     */;
    _proto._adjustDialog = function _adjustDialog() {
      var isModalOverflowing = this._element.scrollHeight > document.documentElement.clientHeight;
      var scrollbarWidth = this._scrollBar.getWidth();
      var isBodyOverflowing = scrollbarWidth > 0;
      if (isBodyOverflowing && !isModalOverflowing) {
        var property = isRTL() ? 'paddingLeft' : 'paddingRight';
        this._element.style[property] = scrollbarWidth + "px";
      }
      if (!isBodyOverflowing && isModalOverflowing) {
        var _property = isRTL() ? 'paddingRight' : 'paddingLeft';
        this._element.style[_property] = scrollbarWidth + "px";
      }
    };
    _proto._resetAdjustments = function _resetAdjustments() {
      this._element.style.paddingLeft = '';
      this._element.style.paddingRight = '';
    }

    // Static
    ;
    Modal.jQueryInterface = function jQueryInterface(config, relatedTarget) {
      return this.each(function () {
        var data = Modal.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config](relatedTarget);
      });
    };
    _createClass(Modal, null, [{
      key: "Default",
      get: function get() {
        return Default$6;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$6;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$7;
      }
    }]);
    return Modal;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API$2, SELECTOR_DATA_TOGGLE$2, function (event) {
    var _this8 = this;
    var target = SelectorEngine.getElementFromSelector(this);
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    EventHandler.one(target, EVENT_SHOW$4, function (showEvent) {
      if (showEvent.defaultPrevented) {
        // only register focus restorer if modal will actually get shown
        return;
      }
      EventHandler.one(target, EVENT_HIDDEN$4, function () {
        if (isVisible(_this8)) {
          _this8.focus();
        }
      });
    });

    // avoid conflict when clicking modal toggler while another one is open
    var alreadyOpen = SelectorEngine.findOne(OPEN_SELECTOR$1);
    if (alreadyOpen) {
      Modal.getInstance(alreadyOpen).hide();
    }
    var data = Modal.getOrCreateInstance(target);
    data.toggle(this);
  });
  enableDismissTrigger(Modal);

  /**
   * jQuery
   */

  defineJQueryPlugin(Modal);

  /**
   * Constants
   */

  var NAME$6 = 'offcanvas';
  var DATA_KEY$3 = 'bs.offcanvas';
  var EVENT_KEY$3 = "." + DATA_KEY$3;
  var DATA_API_KEY$1 = '.data-api';
  var EVENT_LOAD_DATA_API$2 = "load" + EVENT_KEY$3 + DATA_API_KEY$1;
  var ESCAPE_KEY = 'Escape';
  var CLASS_NAME_SHOW$3 = 'show';
  var CLASS_NAME_SHOWING$1 = 'showing';
  var CLASS_NAME_HIDING = 'hiding';
  var CLASS_NAME_BACKDROP = 'offcanvas-backdrop';
  var OPEN_SELECTOR = '.offcanvas.show';
  var EVENT_SHOW$3 = "show" + EVENT_KEY$3;
  var EVENT_SHOWN$3 = "shown" + EVENT_KEY$3;
  var EVENT_HIDE$3 = "hide" + EVENT_KEY$3;
  var EVENT_HIDE_PREVENTED = "hidePrevented" + EVENT_KEY$3;
  var EVENT_HIDDEN$3 = "hidden" + EVENT_KEY$3;
  var EVENT_RESIZE = "resize" + EVENT_KEY$3;
  var EVENT_CLICK_DATA_API$1 = "click" + EVENT_KEY$3 + DATA_API_KEY$1;
  var EVENT_KEYDOWN_DISMISS = "keydown.dismiss" + EVENT_KEY$3;
  var SELECTOR_DATA_TOGGLE$1 = '[data-bs-toggle="offcanvas"]';
  var Default$5 = {
    backdrop: true,
    keyboard: true,
    scroll: false
  };
  var DefaultType$5 = {
    backdrop: '(boolean|string)',
    keyboard: 'boolean',
    scroll: 'boolean'
  };

  /**
   * Class definition
   */
  var Offcanvas = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Offcanvas, _BaseComponent);
    function Offcanvas(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._isShown = false;
      _this._backdrop = _this._initializeBackDrop();
      _this._focustrap = _this._initializeFocusTrap();
      _this._addEventListeners();
      return _this;
    }

    // Getters
    var _proto = Offcanvas.prototype;
    // Public
    _proto.toggle = function toggle(relatedTarget) {
      return this._isShown ? this.hide() : this.show(relatedTarget);
    };
    _proto.show = function show(relatedTarget) {
      var _this2 = this;
      if (this._isShown) {
        return;
      }
      var showEvent = EventHandler.trigger(this._element, EVENT_SHOW$3, {
        relatedTarget: relatedTarget
      });
      if (showEvent.defaultPrevented) {
        return;
      }
      this._isShown = true;
      this._backdrop.show();
      if (!this._config.scroll) {
        new ScrollBarHelper().hide();
      }
      this._element.setAttribute('aria-modal', true);
      this._element.setAttribute('role', 'dialog');
      this._element.classList.add(CLASS_NAME_SHOWING$1);
      var completeCallBack = function completeCallBack() {
        if (!_this2._config.scroll || _this2._config.backdrop) {
          _this2._focustrap.activate();
        }
        _this2._element.classList.add(CLASS_NAME_SHOW$3);
        _this2._element.classList.remove(CLASS_NAME_SHOWING$1);
        EventHandler.trigger(_this2._element, EVENT_SHOWN$3, {
          relatedTarget: relatedTarget
        });
      };
      this._queueCallback(completeCallBack, this._element, true);
    };
    _proto.hide = function hide() {
      var _this3 = this;
      if (!this._isShown) {
        return;
      }
      var hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$3);
      if (hideEvent.defaultPrevented) {
        return;
      }
      this._focustrap.deactivate();
      this._element.blur();
      this._isShown = false;
      this._element.classList.add(CLASS_NAME_HIDING);
      this._backdrop.hide();
      var completeCallback = function completeCallback() {
        _this3._element.classList.remove(CLASS_NAME_SHOW$3, CLASS_NAME_HIDING);
        _this3._element.removeAttribute('aria-modal');
        _this3._element.removeAttribute('role');
        if (!_this3._config.scroll) {
          new ScrollBarHelper().reset();
        }
        EventHandler.trigger(_this3._element, EVENT_HIDDEN$3);
      };
      this._queueCallback(completeCallback, this._element, true);
    };
    _proto.dispose = function dispose() {
      this._backdrop.dispose();
      this._focustrap.deactivate();
      _BaseComponent.prototype.dispose.call(this);
    }

    // Private
    ;
    _proto._initializeBackDrop = function _initializeBackDrop() {
      var _this4 = this;
      var clickCallback = function clickCallback() {
        if (_this4._config.backdrop === 'static') {
          EventHandler.trigger(_this4._element, EVENT_HIDE_PREVENTED);
          return;
        }
        _this4.hide();
      };

      // 'static' option will be translated to true, and booleans will keep their value
      var isVisible = Boolean(this._config.backdrop);
      return new Backdrop({
        className: CLASS_NAME_BACKDROP,
        isVisible: isVisible,
        isAnimated: true,
        rootElement: this._element.parentNode,
        clickCallback: isVisible ? clickCallback : null
      });
    };
    _proto._initializeFocusTrap = function _initializeFocusTrap() {
      return new FocusTrap({
        trapElement: this._element
      });
    };
    _proto._addEventListeners = function _addEventListeners() {
      var _this5 = this;
      EventHandler.on(this._element, EVENT_KEYDOWN_DISMISS, function (event) {
        if (event.key !== ESCAPE_KEY) {
          return;
        }
        if (_this5._config.keyboard) {
          _this5.hide();
          return;
        }
        EventHandler.trigger(_this5._element, EVENT_HIDE_PREVENTED);
      });
    }

    // Static
    ;
    Offcanvas.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Offcanvas.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config](this);
      });
    };
    _createClass(Offcanvas, null, [{
      key: "Default",
      get: function get() {
        return Default$5;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$5;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$6;
      }
    }]);
    return Offcanvas;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API$1, SELECTOR_DATA_TOGGLE$1, function (event) {
    var _this6 = this;
    var target = SelectorEngine.getElementFromSelector(this);
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    if (isDisabled(this)) {
      return;
    }
    EventHandler.one(target, EVENT_HIDDEN$3, function () {
      // focus on trigger when it is closed
      if (isVisible(_this6)) {
        _this6.focus();
      }
    });

    // avoid conflict when clicking a toggler of an offcanvas, while another is open
    var alreadyOpen = SelectorEngine.findOne(OPEN_SELECTOR);
    if (alreadyOpen && alreadyOpen !== target) {
      Offcanvas.getInstance(alreadyOpen).hide();
    }
    var data = Offcanvas.getOrCreateInstance(target);
    data.toggle(this);
  });
  EventHandler.on(window, EVENT_LOAD_DATA_API$2, function () {
    for (var _iterator = _createForOfIteratorHelperLoose(SelectorEngine.find(OPEN_SELECTOR)), _step; !(_step = _iterator()).done;) {
      var selector = _step.value;
      Offcanvas.getOrCreateInstance(selector).show();
    }
  });
  EventHandler.on(window, EVENT_RESIZE, function () {
    for (var _iterator2 = _createForOfIteratorHelperLoose(SelectorEngine.find('[aria-modal][class*=show][class*=offcanvas-]')), _step2; !(_step2 = _iterator2()).done;) {
      var element = _step2.value;
      if (getComputedStyle(element).position !== 'fixed') {
        Offcanvas.getOrCreateInstance(element).hide();
      }
    }
  });
  enableDismissTrigger(Offcanvas);

  /**
   * jQuery
   */

  defineJQueryPlugin(Offcanvas);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/sanitizer.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  // js-docs-start allow-list
  var ARIA_ATTRIBUTE_PATTERN = /^aria-[\w-]*$/i;
  var DefaultAllowlist = {
    // Global attributes allowed on any supplied element below.
    '*': ['class', 'dir', 'id', 'lang', 'role', ARIA_ATTRIBUTE_PATTERN],
    a: ['target', 'href', 'title', 'rel'],
    area: [],
    b: [],
    br: [],
    col: [],
    code: [],
    dd: [],
    div: [],
    dl: [],
    dt: [],
    em: [],
    hr: [],
    h1: [],
    h2: [],
    h3: [],
    h4: [],
    h5: [],
    h6: [],
    i: [],
    img: ['src', 'srcset', 'alt', 'title', 'width', 'height'],
    li: [],
    ol: [],
    p: [],
    pre: [],
    s: [],
    small: [],
    span: [],
    sub: [],
    sup: [],
    strong: [],
    u: [],
    ul: []
  };
  // js-docs-end allow-list

  var uriAttributes = new Set(['background', 'cite', 'href', 'itemtype', 'longdesc', 'poster', 'src', 'xlink:href']);

  /**
   * A pattern that recognizes URLs that are safe wrt. XSS in URL navigation
   * contexts.
   *
   * Shout-out to Angular https://github.com/angular/angular/blob/15.2.8/packages/core/src/sanitization/url_sanitizer.ts#L38
   */
  var SAFE_URL_PATTERN = /^(?!javascript:)(?:[a-z0-9+.-]+:|[^&:/?#]*(?:[/?#]|$))/i;
  var allowedAttribute = function allowedAttribute(attribute, allowedAttributeList) {
    var attributeName = attribute.nodeName.toLowerCase();
    if (allowedAttributeList.includes(attributeName)) {
      if (uriAttributes.has(attributeName)) {
        return Boolean(SAFE_URL_PATTERN.test(attribute.nodeValue));
      }
      return true;
    }

    // Check if a regular expression validates the attribute.
    return allowedAttributeList.filter(function (attributeRegex) {
      return attributeRegex instanceof RegExp;
    }).some(function (regex) {
      return regex.test(attributeName);
    });
  };
  function sanitizeHtml(unsafeHtml, allowList, sanitizeFunction) {
    var _ref;
    if (!unsafeHtml.length) {
      return unsafeHtml;
    }
    if (sanitizeFunction && typeof sanitizeFunction === 'function') {
      return sanitizeFunction(unsafeHtml);
    }
    var domParser = new window.DOMParser();
    var createdDocument = domParser.parseFromString(unsafeHtml, 'text/html');
    var elements = (_ref = []).concat.apply(_ref, createdDocument.body.querySelectorAll('*'));
    for (var _iterator = _createForOfIteratorHelperLoose(elements), _step; !(_step = _iterator()).done;) {
      var _ref2;
      var element = _step.value;
      var elementName = element.nodeName.toLowerCase();
      if (!Object.keys(allowList).includes(elementName)) {
        element.remove();
        continue;
      }
      var attributeList = (_ref2 = []).concat.apply(_ref2, element.attributes);
      var allowedAttributes = [].concat(allowList['*'] || [], allowList[elementName] || []);
      for (var _iterator2 = _createForOfIteratorHelperLoose(attributeList), _step2; !(_step2 = _iterator2()).done;) {
        var attribute = _step2.value;
        if (!allowedAttribute(attribute, allowedAttributes)) {
          element.removeAttribute(attribute.nodeName);
        }
      }
    }
    return createdDocument.body.innerHTML;
  }

  /**
   * Constants
   */

  var NAME$5 = 'TemplateFactory';
  var Default$4 = {
    allowList: DefaultAllowlist,
    content: {},
    // { selector : text ,  selector2 : text2 , }
    extraClass: '',
    html: false,
    sanitize: true,
    sanitizeFn: null,
    template: '<div></div>'
  };
  var DefaultType$4 = {
    allowList: 'object',
    content: 'object',
    extraClass: '(string|function)',
    html: 'boolean',
    sanitize: 'boolean',
    sanitizeFn: '(null|function)',
    template: 'string'
  };
  var DefaultContentType = {
    entry: '(string|element|function|null)',
    selector: '(string|element)'
  };

  /**
   * Class definition
   */
  var TemplateFactory = /*#__PURE__*/function (_Config) {
    _inheritsLoose(TemplateFactory, _Config);
    function TemplateFactory(config) {
      var _this;
      _this = _Config.call(this) || this;
      _this._config = _this._getConfig(config);
      return _this;
    }

    // Getters
    var _proto = TemplateFactory.prototype;
    // Public
    _proto.getContent = function getContent() {
      var _this2 = this;
      return Object.values(this._config.content).map(function (config) {
        return _this2._resolvePossibleFunction(config);
      }).filter(Boolean);
    };
    _proto.hasContent = function hasContent() {
      return this.getContent().length > 0;
    };
    _proto.changeContent = function changeContent(content) {
      this._checkContent(content);
      this._config.content = _extends({}, this._config.content, content);
      return this;
    };
    _proto.toHtml = function toHtml() {
      var templateWrapper = document.createElement('div');
      templateWrapper.innerHTML = this._maybeSanitize(this._config.template);
      for (var _i = 0, _Object$entries = Object.entries(this._config.content); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = _Object$entries[_i],
          selector = _Object$entries$_i[0],
          text = _Object$entries$_i[1];
        this._setContent(templateWrapper, text, selector);
      }
      var template = templateWrapper.children[0];
      var extraClass = this._resolvePossibleFunction(this._config.extraClass);
      if (extraClass) {
        var _template$classList;
        (_template$classList = template.classList).add.apply(_template$classList, extraClass.split(' '));
      }
      return template;
    }

    // Private
    ;
    _proto._typeCheckConfig = function _typeCheckConfig(config) {
      _Config.prototype._typeCheckConfig.call(this, config);
      this._checkContent(config.content);
    };
    _proto._checkContent = function _checkContent(arg) {
      for (var _i2 = 0, _Object$entries2 = Object.entries(arg); _i2 < _Object$entries2.length; _i2++) {
        var _Object$entries2$_i = _Object$entries2[_i2],
          selector = _Object$entries2$_i[0],
          content = _Object$entries2$_i[1];
        _Config.prototype._typeCheckConfig.call(this, {
          selector: selector,
          entry: content
        }, DefaultContentType);
      }
    };
    _proto._setContent = function _setContent(template, content, selector) {
      var templateElement = SelectorEngine.findOne(selector, template);
      if (!templateElement) {
        return;
      }
      content = this._resolvePossibleFunction(content);
      if (!content) {
        templateElement.remove();
        return;
      }
      if (isElement(content)) {
        this._putElementInTemplate(getElement(content), templateElement);
        return;
      }
      if (this._config.html) {
        templateElement.innerHTML = this._maybeSanitize(content);
        return;
      }
      templateElement.textContent = content;
    };
    _proto._maybeSanitize = function _maybeSanitize(arg) {
      return this._config.sanitize ? sanitizeHtml(arg, this._config.allowList, this._config.sanitizeFn) : arg;
    };
    _proto._resolvePossibleFunction = function _resolvePossibleFunction(arg) {
      return execute(arg, [undefined, this]);
    };
    _proto._putElementInTemplate = function _putElementInTemplate(element, templateElement) {
      if (this._config.html) {
        templateElement.innerHTML = '';
        templateElement.append(element);
        return;
      }
      templateElement.textContent = element.textContent;
    };
    _createClass(TemplateFactory, null, [{
      key: "Default",
      get: function get() {
        return Default$4;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$4;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$5;
      }
    }]);
    return TemplateFactory;
  }(Config);

  /**
   * Constants
   */

  var NAME$4 = 'tooltip';
  var DISALLOWED_ATTRIBUTES = new Set(['sanitize', 'allowList', 'sanitizeFn']);
  var CLASS_NAME_FADE$2 = 'fade';
  var CLASS_NAME_MODAL = 'modal';
  var CLASS_NAME_SHOW$2 = 'show';
  var SELECTOR_TOOLTIP_INNER = '.tooltip-inner';
  var SELECTOR_MODAL = "." + CLASS_NAME_MODAL;
  var EVENT_MODAL_HIDE = 'hide.bs.modal';
  var TRIGGER_HOVER = 'hover';
  var TRIGGER_FOCUS = 'focus';
  var TRIGGER_CLICK = 'click';
  var TRIGGER_MANUAL = 'manual';
  var EVENT_HIDE$2 = 'hide';
  var EVENT_HIDDEN$2 = 'hidden';
  var EVENT_SHOW$2 = 'show';
  var EVENT_SHOWN$2 = 'shown';
  var EVENT_INSERTED = 'inserted';
  var EVENT_CLICK$1 = 'click';
  var EVENT_FOCUSIN$1 = 'focusin';
  var EVENT_FOCUSOUT$1 = 'focusout';
  var EVENT_MOUSEENTER = 'mouseenter';
  var EVENT_MOUSELEAVE = 'mouseleave';
  var AttachmentMap = {
    AUTO: 'auto',
    TOP: 'top',
    RIGHT: isRTL() ? 'left' : 'right',
    BOTTOM: 'bottom',
    LEFT: isRTL() ? 'right' : 'left'
  };
  var Default$3 = {
    allowList: DefaultAllowlist,
    animation: true,
    boundary: 'clippingParents',
    container: false,
    customClass: '',
    delay: 0,
    fallbackPlacements: ['top', 'right', 'bottom', 'left'],
    html: false,
    offset: [0, 6],
    placement: 'top',
    popperConfig: null,
    sanitize: true,
    sanitizeFn: null,
    selector: false,
    template: '<div class="tooltip" role="tooltip">' + '<div class="tooltip-arrow"></div>' + '<div class="tooltip-inner"></div>' + '</div>',
    title: '',
    trigger: 'hover focus'
  };
  var DefaultType$3 = {
    allowList: 'object',
    animation: 'boolean',
    boundary: '(string|element)',
    container: '(string|element|boolean)',
    customClass: '(string|function)',
    delay: '(number|object)',
    fallbackPlacements: 'array',
    html: 'boolean',
    offset: '(array|string|function)',
    placement: '(string|function)',
    popperConfig: '(null|object|function)',
    sanitize: 'boolean',
    sanitizeFn: '(null|function)',
    selector: '(string|boolean)',
    template: 'string',
    title: '(string|element|function)',
    trigger: 'string'
  };

  /**
   * Class definition
   */
  var Tooltip = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Tooltip, _BaseComponent);
    function Tooltip(element, config) {
      var _this;
      if (typeof Popper__namespace === 'undefined') {
        throw new TypeError('Bootstrap\'s tooltips require Popper (https://popper.js.org/docs/v2/)');
      }
      _this = _BaseComponent.call(this, element, config) || this;

      // Private
      _this._isEnabled = true;
      _this._timeout = 0;
      _this._isHovered = null;
      _this._activeTrigger = {};
      _this._popper = null;
      _this._templateFactory = null;
      _this._newContent = null;

      // Protected
      _this.tip = null;
      _this._setListeners();
      if (!_this._config.selector) {
        _this._fixTitle();
      }
      return _this;
    }

    // Getters
    var _proto = Tooltip.prototype;
    // Public
    _proto.enable = function enable() {
      this._isEnabled = true;
    };
    _proto.disable = function disable() {
      this._isEnabled = false;
    };
    _proto.toggleEnabled = function toggleEnabled() {
      this._isEnabled = !this._isEnabled;
    };
    _proto.toggle = function toggle() {
      if (!this._isEnabled) {
        return;
      }
      if (this._isShown()) {
        this._leave();
        return;
      }
      this._enter();
    };
    _proto.dispose = function dispose() {
      clearTimeout(this._timeout);
      EventHandler.off(this._element.closest(SELECTOR_MODAL), EVENT_MODAL_HIDE, this._hideModalHandler);
      if (this._element.getAttribute('data-bs-original-title')) {
        this._element.setAttribute('title', this._element.getAttribute('data-bs-original-title'));
      }
      this._disposePopper();
      _BaseComponent.prototype.dispose.call(this);
    };
    _proto.show = function show() {
      var _this2 = this;
      if (this._element.style.display === 'none') {
        throw new Error('Please use show on visible elements');
      }
      if (!(this._isWithContent() && this._isEnabled)) {
        return;
      }
      var showEvent = EventHandler.trigger(this._element, this.constructor.eventName(EVENT_SHOW$2));
      var shadowRoot = findShadowRoot(this._element);
      var isInTheDom = (shadowRoot || this._element.ownerDocument.documentElement).contains(this._element);
      if (showEvent.defaultPrevented || !isInTheDom) {
        return;
      }

      // TODO: v6 remove this or make it optional
      this._disposePopper();
      var tip = this._getTipElement();
      this._element.setAttribute('aria-describedby', tip.getAttribute('id'));
      var container = this._config.container;
      if (!this._element.ownerDocument.documentElement.contains(this.tip)) {
        container.append(tip);
        EventHandler.trigger(this._element, this.constructor.eventName(EVENT_INSERTED));
      }
      this._popper = this._createPopper(tip);
      tip.classList.add(CLASS_NAME_SHOW$2);

      // If this is a touch-enabled device we add extra
      // empty mouseover listeners to the body's immediate children;
      // only needed because of broken event delegation on iOS
      // https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html
      if ('ontouchstart' in document.documentElement) {
        for (var _iterator = _createForOfIteratorHelperLoose((_ref = []).concat.apply(_ref, document.body.children)), _step; !(_step = _iterator()).done;) {
          var _ref;
          var element = _step.value;
          EventHandler.on(element, 'mouseover', noop);
        }
      }
      var complete = function complete() {
        EventHandler.trigger(_this2._element, _this2.constructor.eventName(EVENT_SHOWN$2));
        if (_this2._isHovered === false) {
          _this2._leave();
        }
        _this2._isHovered = false;
      };
      this._queueCallback(complete, this.tip, this._isAnimated());
    };
    _proto.hide = function hide() {
      var _this3 = this;
      if (!this._isShown()) {
        return;
      }
      var hideEvent = EventHandler.trigger(this._element, this.constructor.eventName(EVENT_HIDE$2));
      if (hideEvent.defaultPrevented) {
        return;
      }
      var tip = this._getTipElement();
      tip.classList.remove(CLASS_NAME_SHOW$2);

      // If this is a touch-enabled device we remove the extra
      // empty mouseover listeners we added for iOS support
      if ('ontouchstart' in document.documentElement) {
        for (var _iterator2 = _createForOfIteratorHelperLoose((_ref2 = []).concat.apply(_ref2, document.body.children)), _step2; !(_step2 = _iterator2()).done;) {
          var _ref2;
          var element = _step2.value;
          EventHandler.off(element, 'mouseover', noop);
        }
      }
      this._activeTrigger[TRIGGER_CLICK] = false;
      this._activeTrigger[TRIGGER_FOCUS] = false;
      this._activeTrigger[TRIGGER_HOVER] = false;
      this._isHovered = null; // it is a trick to support manual triggering

      var complete = function complete() {
        if (_this3._isWithActiveTrigger()) {
          return;
        }
        if (!_this3._isHovered) {
          _this3._disposePopper();
        }
        _this3._element.removeAttribute('aria-describedby');
        EventHandler.trigger(_this3._element, _this3.constructor.eventName(EVENT_HIDDEN$2));
      };
      this._queueCallback(complete, this.tip, this._isAnimated());
    };
    _proto.update = function update() {
      if (this._popper) {
        this._popper.update();
      }
    }

    // Protected
    ;
    _proto._isWithContent = function _isWithContent() {
      return Boolean(this._getTitle());
    };
    _proto._getTipElement = function _getTipElement() {
      if (!this.tip) {
        this.tip = this._createTipElement(this._newContent || this._getContentForTemplate());
      }
      return this.tip;
    };
    _proto._createTipElement = function _createTipElement(content) {
      var tip = this._getTemplateFactory(content).toHtml();

      // TODO: remove this check in v6
      if (!tip) {
        return null;
      }
      tip.classList.remove(CLASS_NAME_FADE$2, CLASS_NAME_SHOW$2);
      // TODO: v6 the following can be achieved with CSS only
      tip.classList.add("bs-" + this.constructor.NAME + "-auto");
      var tipId = getUID(this.constructor.NAME).toString();
      tip.setAttribute('id', tipId);
      if (this._isAnimated()) {
        tip.classList.add(CLASS_NAME_FADE$2);
      }
      return tip;
    };
    _proto.setContent = function setContent(content) {
      this._newContent = content;
      if (this._isShown()) {
        this._disposePopper();
        this.show();
      }
    };
    _proto._getTemplateFactory = function _getTemplateFactory(content) {
      if (this._templateFactory) {
        this._templateFactory.changeContent(content);
      } else {
        this._templateFactory = new TemplateFactory(_extends({}, this._config, {
          // the `content` var has to be after `this._config`
          // to override config.content in case of popover
          content: content,
          extraClass: this._resolvePossibleFunction(this._config.customClass)
        }));
      }
      return this._templateFactory;
    };
    _proto._getContentForTemplate = function _getContentForTemplate() {
      var _ref3;
      return _ref3 = {}, _ref3[SELECTOR_TOOLTIP_INNER] = this._getTitle(), _ref3;
    };
    _proto._getTitle = function _getTitle() {
      return this._resolvePossibleFunction(this._config.title) || this._element.getAttribute('data-bs-original-title');
    }

    // Private
    ;
    _proto._initializeOnDelegatedTarget = function _initializeOnDelegatedTarget(event) {
      return this.constructor.getOrCreateInstance(event.delegateTarget, this._getDelegateConfig());
    };
    _proto._isAnimated = function _isAnimated() {
      return this._config.animation || this.tip && this.tip.classList.contains(CLASS_NAME_FADE$2);
    };
    _proto._isShown = function _isShown() {
      return this.tip && this.tip.classList.contains(CLASS_NAME_SHOW$2);
    };
    _proto._createPopper = function _createPopper(tip) {
      var placement = execute(this._config.placement, [this, tip, this._element]);
      var attachment = AttachmentMap[placement.toUpperCase()];
      return Popper__namespace.createPopper(this._element, tip, this._getPopperConfig(attachment));
    };
    _proto._getOffset = function _getOffset() {
      var _this4 = this;
      var offset = this._config.offset;
      if (typeof offset === 'string') {
        return offset.split(',').map(function (value) {
          return Number.parseInt(value, 10);
        });
      }
      if (typeof offset === 'function') {
        return function (popperData) {
          return offset(popperData, _this4._element);
        };
      }
      return offset;
    };
    _proto._resolvePossibleFunction = function _resolvePossibleFunction(arg) {
      return execute(arg, [this._element, this._element]);
    };
    _proto._getPopperConfig = function _getPopperConfig(attachment) {
      var _this5 = this;
      var defaultBsPopperConfig = {
        placement: attachment,
        modifiers: [{
          name: 'flip',
          options: {
            fallbackPlacements: this._config.fallbackPlacements
          }
        }, {
          name: 'offset',
          options: {
            offset: this._getOffset()
          }
        }, {
          name: 'preventOverflow',
          options: {
            boundary: this._config.boundary
          }
        }, {
          name: 'arrow',
          options: {
            element: "." + this.constructor.NAME + "-arrow"
          }
        }, {
          name: 'preSetPlacement',
          enabled: true,
          phase: 'beforeMain',
          fn: function fn(data) {
            // Pre-set Popper's placement attribute in order to read the arrow sizes properly.
            // Otherwise, Popper mixes up the width and height dimensions since the initial arrow style is for top placement
            _this5._getTipElement().setAttribute('data-popper-placement', data.state.placement);
          }
        }]
      };
      return _extends({}, defaultBsPopperConfig, execute(this._config.popperConfig, [undefined, defaultBsPopperConfig]));
    };
    _proto._setListeners = function _setListeners() {
      var _this6 = this;
      var triggers = this._config.trigger.split(' ');
      for (var _iterator3 = _createForOfIteratorHelperLoose(triggers), _step3; !(_step3 = _iterator3()).done;) {
        var trigger = _step3.value;
        if (trigger === 'click') {
          EventHandler.on(this._element, this.constructor.eventName(EVENT_CLICK$1), this._config.selector, function (event) {
            var context = _this6._initializeOnDelegatedTarget(event);
            context._activeTrigger[TRIGGER_CLICK] = !(context._isShown() && context._activeTrigger[TRIGGER_CLICK]);
            context.toggle();
          });
        } else if (trigger !== TRIGGER_MANUAL) {
          var eventIn = trigger === TRIGGER_HOVER ? this.constructor.eventName(EVENT_MOUSEENTER) : this.constructor.eventName(EVENT_FOCUSIN$1);
          var eventOut = trigger === TRIGGER_HOVER ? this.constructor.eventName(EVENT_MOUSELEAVE) : this.constructor.eventName(EVENT_FOCUSOUT$1);
          EventHandler.on(this._element, eventIn, this._config.selector, function (event) {
            var context = _this6._initializeOnDelegatedTarget(event);
            context._activeTrigger[event.type === 'focusin' ? TRIGGER_FOCUS : TRIGGER_HOVER] = true;
            context._enter();
          });
          EventHandler.on(this._element, eventOut, this._config.selector, function (event) {
            var context = _this6._initializeOnDelegatedTarget(event);
            context._activeTrigger[event.type === 'focusout' ? TRIGGER_FOCUS : TRIGGER_HOVER] = context._element.contains(event.relatedTarget);
            context._leave();
          });
        }
      }
      this._hideModalHandler = function () {
        if (_this6._element) {
          _this6.hide();
        }
      };
      EventHandler.on(this._element.closest(SELECTOR_MODAL), EVENT_MODAL_HIDE, this._hideModalHandler);
    };
    _proto._fixTitle = function _fixTitle() {
      var title = this._element.getAttribute('title');
      if (!title) {
        return;
      }
      if (!this._element.getAttribute('aria-label') && !this._element.textContent.trim()) {
        this._element.setAttribute('aria-label', title);
      }
      this._element.setAttribute('data-bs-original-title', title); // DO NOT USE IT. Is only for backwards compatibility
      this._element.removeAttribute('title');
    };
    _proto._enter = function _enter() {
      var _this7 = this;
      if (this._isShown() || this._isHovered) {
        this._isHovered = true;
        return;
      }
      this._isHovered = true;
      this._setTimeout(function () {
        if (_this7._isHovered) {
          _this7.show();
        }
      }, this._config.delay.show);
    };
    _proto._leave = function _leave() {
      var _this8 = this;
      if (this._isWithActiveTrigger()) {
        return;
      }
      this._isHovered = false;
      this._setTimeout(function () {
        if (!_this8._isHovered) {
          _this8.hide();
        }
      }, this._config.delay.hide);
    };
    _proto._setTimeout = function _setTimeout(handler, timeout) {
      clearTimeout(this._timeout);
      this._timeout = setTimeout(handler, timeout);
    };
    _proto._isWithActiveTrigger = function _isWithActiveTrigger() {
      return Object.values(this._activeTrigger).includes(true);
    };
    _proto._getConfig = function _getConfig(config) {
      var dataAttributes = Manipulator.getDataAttributes(this._element);
      for (var _i = 0, _Object$keys = Object.keys(dataAttributes); _i < _Object$keys.length; _i++) {
        var dataAttribute = _Object$keys[_i];
        if (DISALLOWED_ATTRIBUTES.has(dataAttribute)) {
          delete dataAttributes[dataAttribute];
        }
      }
      config = _extends({}, dataAttributes, typeof config === 'object' && config ? config : {});
      config = this._mergeConfigObj(config);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    };
    _proto._configAfterMerge = function _configAfterMerge(config) {
      config.container = config.container === false ? document.body : getElement(config.container);
      if (typeof config.delay === 'number') {
        config.delay = {
          show: config.delay,
          hide: config.delay
        };
      }
      if (typeof config.title === 'number') {
        config.title = config.title.toString();
      }
      if (typeof config.content === 'number') {
        config.content = config.content.toString();
      }
      return config;
    };
    _proto._getDelegateConfig = function _getDelegateConfig() {
      var config = {};
      for (var _i2 = 0, _Object$entries = Object.entries(this._config); _i2 < _Object$entries.length; _i2++) {
        var _Object$entries$_i = _Object$entries[_i2],
          key = _Object$entries$_i[0],
          value = _Object$entries$_i[1];
        if (this.constructor.Default[key] !== value) {
          config[key] = value;
        }
      }
      config.selector = false;
      config.trigger = 'manual';

      // In the future can be replaced with:
      // const keysWithDifferentValues = Object.entries(this._config).filter(entry => this.constructor.Default[entry[0]] !== this._config[entry[0]])
      // `Object.fromEntries(keysWithDifferentValues)`
      return config;
    };
    _proto._disposePopper = function _disposePopper() {
      if (this._popper) {
        this._popper.destroy();
        this._popper = null;
      }
      if (this.tip) {
        this.tip.remove();
        this.tip = null;
      }
    }

    // Static
    ;
    Tooltip.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Tooltip.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config]();
      });
    };
    _createClass(Tooltip, null, [{
      key: "Default",
      get: function get() {
        return Default$3;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$3;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$4;
      }
    }]);
    return Tooltip;
  }(BaseComponent);
  /**
   * jQuery
   */
  defineJQueryPlugin(Tooltip);

  /**
   * Constants
   */

  var NAME$3 = 'popover';
  var SELECTOR_TITLE = '.popover-header';
  var SELECTOR_CONTENT = '.popover-body';
  var Default$2 = _extends({}, Tooltip.Default, {
    content: '',
    offset: [0, 8],
    placement: 'right',
    template: '<div class="popover" role="tooltip">' + '<div class="popover-arrow"></div>' + '<h3 class="popover-header"></h3>' + '<div class="popover-body"></div>' + '</div>',
    trigger: 'click'
  });
  var DefaultType$2 = _extends({}, Tooltip.DefaultType, {
    content: '(null|string|element|function)'
  });

  /**
   * Class definition
   */
  var Popover = /*#__PURE__*/function (_Tooltip) {
    _inheritsLoose(Popover, _Tooltip);
    function Popover() {
      return _Tooltip.apply(this, arguments) || this;
    }
    var _proto = Popover.prototype;
    // Overrides
    _proto._isWithContent = function _isWithContent() {
      return this._getTitle() || this._getContent();
    }

    // Private
    ;
    _proto._getContentForTemplate = function _getContentForTemplate() {
      var _ref;
      return _ref = {}, _ref[SELECTOR_TITLE] = this._getTitle(), _ref[SELECTOR_CONTENT] = this._getContent(), _ref;
    };
    _proto._getContent = function _getContent() {
      return this._resolvePossibleFunction(this._config.content);
    }

    // Static
    ;
    Popover.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Popover.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config]();
      });
    };
    _createClass(Popover, null, [{
      key: "Default",
      get:
      // Getters
      function get() {
        return Default$2;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$2;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$3;
      }
    }]);
    return Popover;
  }(Tooltip);
  /**
   * jQuery
   */
  defineJQueryPlugin(Popover);

  /**
   * Constants
   */

  var NAME$2 = 'scrollspy';
  var DATA_KEY$2 = 'bs.scrollspy';
  var EVENT_KEY$2 = "." + DATA_KEY$2;
  var DATA_API_KEY = '.data-api';
  var EVENT_ACTIVATE = "activate" + EVENT_KEY$2;
  var EVENT_CLICK = "click" + EVENT_KEY$2;
  var EVENT_LOAD_DATA_API$1 = "load" + EVENT_KEY$2 + DATA_API_KEY;
  var CLASS_NAME_DROPDOWN_ITEM = 'dropdown-item';
  var CLASS_NAME_ACTIVE$1 = 'active';
  var SELECTOR_DATA_SPY = '[data-bs-spy="scroll"]';
  var SELECTOR_TARGET_LINKS = '[href]';
  var SELECTOR_NAV_LIST_GROUP = '.nav, .list-group';
  var SELECTOR_NAV_LINKS = '.nav-link';
  var SELECTOR_NAV_ITEMS = '.nav-item';
  var SELECTOR_LIST_ITEMS = '.list-group-item';
  var SELECTOR_LINK_ITEMS = SELECTOR_NAV_LINKS + ", " + SELECTOR_NAV_ITEMS + " > " + SELECTOR_NAV_LINKS + ", " + SELECTOR_LIST_ITEMS;
  var SELECTOR_DROPDOWN = '.dropdown';
  var SELECTOR_DROPDOWN_TOGGLE$1 = '.dropdown-toggle';
  var Default$1 = {
    offset: null,
    // TODO: v6 @deprecated, keep it for backwards compatibility reasons
    rootMargin: '0px 0px -25%',
    smoothScroll: false,
    target: null,
    threshold: [0.1, 0.5, 1]
  };
  var DefaultType$1 = {
    offset: '(number|null)',
    // TODO v6 @deprecated, keep it for backwards compatibility reasons
    rootMargin: 'string',
    smoothScroll: 'boolean',
    target: 'element',
    threshold: 'array'
  };

  /**
   * Class definition
   */
  var ScrollSpy = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(ScrollSpy, _BaseComponent);
    function ScrollSpy(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;

      // this._element is the observablesContainer and config.target the menu links wrapper
      _this._targetLinks = new Map();
      _this._observableSections = new Map();
      _this._rootElement = getComputedStyle(_this._element).overflowY === 'visible' ? null : _this._element;
      _this._activeTarget = null;
      _this._observer = null;
      _this._previousScrollData = {
        visibleEntryTop: 0,
        parentScrollTop: 0
      };
      _this.refresh(); // initialize
      return _this;
    }

    // Getters
    var _proto = ScrollSpy.prototype;
    // Public
    _proto.refresh = function refresh() {
      this._initializeTargetsAndObservables();
      this._maybeEnableSmoothScroll();
      if (this._observer) {
        this._observer.disconnect();
      } else {
        this._observer = this._getNewObserver();
      }
      for (var _iterator = _createForOfIteratorHelperLoose(this._observableSections.values()), _step; !(_step = _iterator()).done;) {
        var section = _step.value;
        this._observer.observe(section);
      }
    };
    _proto.dispose = function dispose() {
      this._observer.disconnect();
      _BaseComponent.prototype.dispose.call(this);
    }

    // Private
    ;
    _proto._configAfterMerge = function _configAfterMerge(config) {
      // TODO: on v6 target should be given explicitly & remove the {target: 'ss-target'} case
      config.target = getElement(config.target) || document.body;

      // TODO: v6 Only for backwards compatibility reasons. Use rootMargin only
      config.rootMargin = config.offset ? config.offset + "px 0px -30%" : config.rootMargin;
      if (typeof config.threshold === 'string') {
        config.threshold = config.threshold.split(',').map(function (value) {
          return Number.parseFloat(value);
        });
      }
      return config;
    };
    _proto._maybeEnableSmoothScroll = function _maybeEnableSmoothScroll() {
      var _this2 = this;
      if (!this._config.smoothScroll) {
        return;
      }

      // unregister any previous listeners
      EventHandler.off(this._config.target, EVENT_CLICK);
      EventHandler.on(this._config.target, EVENT_CLICK, SELECTOR_TARGET_LINKS, function (event) {
        var observableSection = _this2._observableSections.get(event.target.hash);
        if (observableSection) {
          event.preventDefault();
          var root = _this2._rootElement || window;
          var height = observableSection.offsetTop - _this2._element.offsetTop;
          if (root.scrollTo) {
            root.scrollTo({
              top: height,
              behavior: 'smooth'
            });
            return;
          }

          // Chrome 60 doesn't support `scrollTo`
          root.scrollTop = height;
        }
      });
    };
    _proto._getNewObserver = function _getNewObserver() {
      var _this3 = this;
      var options = {
        root: this._rootElement,
        threshold: this._config.threshold,
        rootMargin: this._config.rootMargin
      };
      return new IntersectionObserver(function (entries) {
        return _this3._observerCallback(entries);
      }, options);
    }

    // The logic of selection
    ;
    _proto._observerCallback = function _observerCallback(entries) {
      var _this4 = this;
      var targetElement = function targetElement(entry) {
        return _this4._targetLinks.get("#" + entry.target.id);
      };
      var activate = function activate(entry) {
        _this4._previousScrollData.visibleEntryTop = entry.target.offsetTop;
        _this4._process(targetElement(entry));
      };
      var parentScrollTop = (this._rootElement || document.documentElement).scrollTop;
      var userScrollsDown = parentScrollTop >= this._previousScrollData.parentScrollTop;
      this._previousScrollData.parentScrollTop = parentScrollTop;
      for (var _iterator2 = _createForOfIteratorHelperLoose(entries), _step2; !(_step2 = _iterator2()).done;) {
        var entry = _step2.value;
        if (!entry.isIntersecting) {
          this._activeTarget = null;
          this._clearActiveClass(targetElement(entry));
          continue;
        }
        var entryIsLowerThanPrevious = entry.target.offsetTop >= this._previousScrollData.visibleEntryTop;
        // if we are scrolling down, pick the bigger offsetTop
        if (userScrollsDown && entryIsLowerThanPrevious) {
          activate(entry);
          // if parent isn't scrolled, let's keep the first visible item, breaking the iteration
          if (!parentScrollTop) {
            return;
          }
          continue;
        }

        // if we are scrolling up, pick the smallest offsetTop
        if (!userScrollsDown && !entryIsLowerThanPrevious) {
          activate(entry);
        }
      }
    };
    _proto._initializeTargetsAndObservables = function _initializeTargetsAndObservables() {
      this._targetLinks = new Map();
      this._observableSections = new Map();
      var targetLinks = SelectorEngine.find(SELECTOR_TARGET_LINKS, this._config.target);
      for (var _iterator3 = _createForOfIteratorHelperLoose(targetLinks), _step3; !(_step3 = _iterator3()).done;) {
        var anchor = _step3.value;
        // ensure that the anchor has an id and is not disabled
        if (!anchor.hash || isDisabled(anchor)) {
          continue;
        }
        var observableSection = SelectorEngine.findOne(decodeURI(anchor.hash), this._element);

        // ensure that the observableSection exists & is visible
        if (isVisible(observableSection)) {
          this._targetLinks.set(decodeURI(anchor.hash), anchor);
          this._observableSections.set(anchor.hash, observableSection);
        }
      }
    };
    _proto._process = function _process(target) {
      if (this._activeTarget === target) {
        return;
      }
      this._clearActiveClass(this._config.target);
      this._activeTarget = target;
      target.classList.add(CLASS_NAME_ACTIVE$1);
      this._activateParents(target);
      EventHandler.trigger(this._element, EVENT_ACTIVATE, {
        relatedTarget: target
      });
    };
    _proto._activateParents = function _activateParents(target) {
      // Activate dropdown parents
      if (target.classList.contains(CLASS_NAME_DROPDOWN_ITEM)) {
        SelectorEngine.findOne(SELECTOR_DROPDOWN_TOGGLE$1, target.closest(SELECTOR_DROPDOWN)).classList.add(CLASS_NAME_ACTIVE$1);
        return;
      }
      for (var _iterator4 = _createForOfIteratorHelperLoose(SelectorEngine.parents(target, SELECTOR_NAV_LIST_GROUP)), _step4; !(_step4 = _iterator4()).done;) {
        var listGroup = _step4.value;
        // Set triggered links parents as active
        // With both <ul> and <nav> markup a parent is the previous sibling of any nav ancestor
        for (var _iterator5 = _createForOfIteratorHelperLoose(SelectorEngine.prev(listGroup, SELECTOR_LINK_ITEMS)), _step5; !(_step5 = _iterator5()).done;) {
          var item = _step5.value;
          item.classList.add(CLASS_NAME_ACTIVE$1);
        }
      }
    };
    _proto._clearActiveClass = function _clearActiveClass(parent) {
      parent.classList.remove(CLASS_NAME_ACTIVE$1);
      var activeNodes = SelectorEngine.find(SELECTOR_TARGET_LINKS + "." + CLASS_NAME_ACTIVE$1, parent);
      for (var _iterator6 = _createForOfIteratorHelperLoose(activeNodes), _step6; !(_step6 = _iterator6()).done;) {
        var node = _step6.value;
        node.classList.remove(CLASS_NAME_ACTIVE$1);
      }
    }

    // Static
    ;
    ScrollSpy.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = ScrollSpy.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config]();
      });
    };
    _createClass(ScrollSpy, null, [{
      key: "Default",
      get: function get() {
        return Default$1;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType$1;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME$2;
      }
    }]);
    return ScrollSpy;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(window, EVENT_LOAD_DATA_API$1, function () {
    for (var _iterator7 = _createForOfIteratorHelperLoose(SelectorEngine.find(SELECTOR_DATA_SPY)), _step7; !(_step7 = _iterator7()).done;) {
      var spy = _step7.value;
      ScrollSpy.getOrCreateInstance(spy);
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(ScrollSpy);

  /**
   * Constants
   */

  var NAME$1 = 'tab';
  var DATA_KEY$1 = 'bs.tab';
  var EVENT_KEY$1 = "." + DATA_KEY$1;
  var EVENT_HIDE$1 = "hide" + EVENT_KEY$1;
  var EVENT_HIDDEN$1 = "hidden" + EVENT_KEY$1;
  var EVENT_SHOW$1 = "show" + EVENT_KEY$1;
  var EVENT_SHOWN$1 = "shown" + EVENT_KEY$1;
  var EVENT_CLICK_DATA_API = "click" + EVENT_KEY$1;
  var EVENT_KEYDOWN = "keydown" + EVENT_KEY$1;
  var EVENT_LOAD_DATA_API = "load" + EVENT_KEY$1;
  var ARROW_LEFT_KEY = 'ArrowLeft';
  var ARROW_RIGHT_KEY = 'ArrowRight';
  var ARROW_UP_KEY = 'ArrowUp';
  var ARROW_DOWN_KEY = 'ArrowDown';
  var HOME_KEY = 'Home';
  var END_KEY = 'End';
  var CLASS_NAME_ACTIVE = 'active';
  var CLASS_NAME_FADE$1 = 'fade';
  var CLASS_NAME_SHOW$1 = 'show';
  var CLASS_DROPDOWN = 'dropdown';
  var SELECTOR_DROPDOWN_TOGGLE = '.dropdown-toggle';
  var SELECTOR_DROPDOWN_MENU = '.dropdown-menu';
  var NOT_SELECTOR_DROPDOWN_TOGGLE = ":not(" + SELECTOR_DROPDOWN_TOGGLE + ")";
  var SELECTOR_TAB_PANEL = '.list-group, .nav, [role="tablist"]';
  var SELECTOR_OUTER = '.nav-item, .list-group-item';
  var SELECTOR_INNER = ".nav-link" + NOT_SELECTOR_DROPDOWN_TOGGLE + ", .list-group-item" + NOT_SELECTOR_DROPDOWN_TOGGLE + ", [role=\"tab\"]" + NOT_SELECTOR_DROPDOWN_TOGGLE;
  var SELECTOR_DATA_TOGGLE = '[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]'; // TODO: could only be `tab` in v6
  var SELECTOR_INNER_ELEM = SELECTOR_INNER + ", " + SELECTOR_DATA_TOGGLE;
  var SELECTOR_DATA_TOGGLE_ACTIVE = "." + CLASS_NAME_ACTIVE + "[data-bs-toggle=\"tab\"], ." + CLASS_NAME_ACTIVE + "[data-bs-toggle=\"pill\"], ." + CLASS_NAME_ACTIVE + "[data-bs-toggle=\"list\"]";

  /**
   * Class definition
   */
  var Tab = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Tab, _BaseComponent);
    function Tab(element) {
      var _this;
      _this = _BaseComponent.call(this, element) || this;
      _this._parent = _this._element.closest(SELECTOR_TAB_PANEL);
      if (!_this._parent) {
        return _assertThisInitialized(_this);
        // TODO: should throw exception in v6
        // throw new TypeError(`${element.outerHTML} has not a valid parent ${SELECTOR_INNER_ELEM}`)
      }

      // Set up initial aria attributes
      _this._setInitialAttributes(_this._parent, _this._getChildren());
      EventHandler.on(_this._element, EVENT_KEYDOWN, function (event) {
        return _this._keydown(event);
      });
      return _this;
    }

    // Getters
    var _proto = Tab.prototype;
    // Public
    _proto.show = function show() {
      // Shows this elem and deactivate the active sibling if exists
      var innerElem = this._element;
      if (this._elemIsActive(innerElem)) {
        return;
      }

      // Search for active tab on same parent to deactivate it
      var active = this._getActiveElem();
      var hideEvent = active ? EventHandler.trigger(active, EVENT_HIDE$1, {
        relatedTarget: innerElem
      }) : null;
      var showEvent = EventHandler.trigger(innerElem, EVENT_SHOW$1, {
        relatedTarget: active
      });
      if (showEvent.defaultPrevented || hideEvent && hideEvent.defaultPrevented) {
        return;
      }
      this._deactivate(active, innerElem);
      this._activate(innerElem, active);
    }

    // Private
    ;
    _proto._activate = function _activate(element, relatedElem) {
      var _this2 = this;
      if (!element) {
        return;
      }
      element.classList.add(CLASS_NAME_ACTIVE);
      this._activate(SelectorEngine.getElementFromSelector(element)); // Search and activate/show the proper section

      var complete = function complete() {
        if (element.getAttribute('role') !== 'tab') {
          element.classList.add(CLASS_NAME_SHOW$1);
          return;
        }
        element.removeAttribute('tabindex');
        element.setAttribute('aria-selected', true);
        _this2._toggleDropDown(element, true);
        EventHandler.trigger(element, EVENT_SHOWN$1, {
          relatedTarget: relatedElem
        });
      };
      this._queueCallback(complete, element, element.classList.contains(CLASS_NAME_FADE$1));
    };
    _proto._deactivate = function _deactivate(element, relatedElem) {
      var _this3 = this;
      if (!element) {
        return;
      }
      element.classList.remove(CLASS_NAME_ACTIVE);
      element.blur();
      this._deactivate(SelectorEngine.getElementFromSelector(element)); // Search and deactivate the shown section too

      var complete = function complete() {
        if (element.getAttribute('role') !== 'tab') {
          element.classList.remove(CLASS_NAME_SHOW$1);
          return;
        }
        element.setAttribute('aria-selected', false);
        element.setAttribute('tabindex', '-1');
        _this3._toggleDropDown(element, false);
        EventHandler.trigger(element, EVENT_HIDDEN$1, {
          relatedTarget: relatedElem
        });
      };
      this._queueCallback(complete, element, element.classList.contains(CLASS_NAME_FADE$1));
    };
    _proto._keydown = function _keydown(event) {
      if (![ARROW_LEFT_KEY, ARROW_RIGHT_KEY, ARROW_UP_KEY, ARROW_DOWN_KEY, HOME_KEY, END_KEY].includes(event.key)) {
        return;
      }
      event.stopPropagation(); // stopPropagation/preventDefault both added to support up/down keys without scrolling the page
      event.preventDefault();
      var children = this._getChildren().filter(function (element) {
        return !isDisabled(element);
      });
      var nextActiveElement;
      if ([HOME_KEY, END_KEY].includes(event.key)) {
        nextActiveElement = children[event.key === HOME_KEY ? 0 : children.length - 1];
      } else {
        var isNext = [ARROW_RIGHT_KEY, ARROW_DOWN_KEY].includes(event.key);
        nextActiveElement = getNextActiveElement(children, event.target, isNext, true);
      }
      if (nextActiveElement) {
        nextActiveElement.focus({
          preventScroll: true
        });
        Tab.getOrCreateInstance(nextActiveElement).show();
      }
    };
    _proto._getChildren = function _getChildren() {
      // collection of inner elements
      return SelectorEngine.find(SELECTOR_INNER_ELEM, this._parent);
    };
    _proto._getActiveElem = function _getActiveElem() {
      var _this4 = this;
      return this._getChildren().find(function (child) {
        return _this4._elemIsActive(child);
      }) || null;
    };
    _proto._setInitialAttributes = function _setInitialAttributes(parent, children) {
      this._setAttributeIfNotExists(parent, 'role', 'tablist');
      for (var _iterator = _createForOfIteratorHelperLoose(children), _step; !(_step = _iterator()).done;) {
        var child = _step.value;
        this._setInitialAttributesOnChild(child);
      }
    };
    _proto._setInitialAttributesOnChild = function _setInitialAttributesOnChild(child) {
      child = this._getInnerElement(child);
      var isActive = this._elemIsActive(child);
      var outerElem = this._getOuterElement(child);
      child.setAttribute('aria-selected', isActive);
      if (outerElem !== child) {
        this._setAttributeIfNotExists(outerElem, 'role', 'presentation');
      }
      if (!isActive) {
        child.setAttribute('tabindex', '-1');
      }
      this._setAttributeIfNotExists(child, 'role', 'tab');

      // set attributes to the related panel too
      this._setInitialAttributesOnTargetPanel(child);
    };
    _proto._setInitialAttributesOnTargetPanel = function _setInitialAttributesOnTargetPanel(child) {
      var target = SelectorEngine.getElementFromSelector(child);
      if (!target) {
        return;
      }
      this._setAttributeIfNotExists(target, 'role', 'tabpanel');
      if (child.id) {
        this._setAttributeIfNotExists(target, 'aria-labelledby', "" + child.id);
      }
    };
    _proto._toggleDropDown = function _toggleDropDown(element, open) {
      var outerElem = this._getOuterElement(element);
      if (!outerElem.classList.contains(CLASS_DROPDOWN)) {
        return;
      }
      var toggle = function toggle(selector, className) {
        var element = SelectorEngine.findOne(selector, outerElem);
        if (element) {
          element.classList.toggle(className, open);
        }
      };
      toggle(SELECTOR_DROPDOWN_TOGGLE, CLASS_NAME_ACTIVE);
      toggle(SELECTOR_DROPDOWN_MENU, CLASS_NAME_SHOW$1);
      outerElem.setAttribute('aria-expanded', open);
    };
    _proto._setAttributeIfNotExists = function _setAttributeIfNotExists(element, attribute, value) {
      if (!element.hasAttribute(attribute)) {
        element.setAttribute(attribute, value);
      }
    };
    _proto._elemIsActive = function _elemIsActive(elem) {
      return elem.classList.contains(CLASS_NAME_ACTIVE);
    }

    // Try to get the inner element (usually the .nav-link)
    ;
    _proto._getInnerElement = function _getInnerElement(elem) {
      return elem.matches(SELECTOR_INNER_ELEM) ? elem : SelectorEngine.findOne(SELECTOR_INNER_ELEM, elem);
    }

    // Try to get the outer element (usually the .nav-item)
    ;
    _proto._getOuterElement = function _getOuterElement(elem) {
      return elem.closest(SELECTOR_OUTER) || elem;
    }

    // Static
    ;
    Tab.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Tab.getOrCreateInstance(this);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError("No method named \"" + config + "\"");
        }
        data[config]();
      });
    };
    _createClass(Tab, null, [{
      key: "NAME",
      get: function get() {
        return NAME$1;
      }
    }]);
    return Tab;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  EventHandler.on(document, EVENT_CLICK_DATA_API, SELECTOR_DATA_TOGGLE, function (event) {
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    if (isDisabled(this)) {
      return;
    }
    Tab.getOrCreateInstance(this).show();
  });

  /**
   * Initialize on focus
   */
  EventHandler.on(window, EVENT_LOAD_DATA_API, function () {
    for (var _iterator2 = _createForOfIteratorHelperLoose(SelectorEngine.find(SELECTOR_DATA_TOGGLE_ACTIVE)), _step2; !(_step2 = _iterator2()).done;) {
      var element = _step2.value;
      Tab.getOrCreateInstance(element);
    }
  });
  /**
   * jQuery
   */

  defineJQueryPlugin(Tab);

  /**
   * Constants
   */

  var NAME = 'toast';
  var DATA_KEY = 'bs.toast';
  var EVENT_KEY = "." + DATA_KEY;
  var EVENT_MOUSEOVER = "mouseover" + EVENT_KEY;
  var EVENT_MOUSEOUT = "mouseout" + EVENT_KEY;
  var EVENT_FOCUSIN = "focusin" + EVENT_KEY;
  var EVENT_FOCUSOUT = "focusout" + EVENT_KEY;
  var EVENT_HIDE = "hide" + EVENT_KEY;
  var EVENT_HIDDEN = "hidden" + EVENT_KEY;
  var EVENT_SHOW = "show" + EVENT_KEY;
  var EVENT_SHOWN = "shown" + EVENT_KEY;
  var CLASS_NAME_FADE = 'fade';
  var CLASS_NAME_HIDE = 'hide'; // @deprecated - kept here only for backwards compatibility
  var CLASS_NAME_SHOW = 'show';
  var CLASS_NAME_SHOWING = 'showing';
  var DefaultType = {
    animation: 'boolean',
    autohide: 'boolean',
    delay: 'number'
  };
  var Default = {
    animation: true,
    autohide: true,
    delay: 5000
  };

  /**
   * Class definition
   */
  var Toast = /*#__PURE__*/function (_BaseComponent) {
    _inheritsLoose(Toast, _BaseComponent);
    function Toast(element, config) {
      var _this;
      _this = _BaseComponent.call(this, element, config) || this;
      _this._timeout = null;
      _this._hasMouseInteraction = false;
      _this._hasKeyboardInteraction = false;
      _this._setListeners();
      return _this;
    }

    // Getters
    var _proto = Toast.prototype;
    // Public
    _proto.show = function show() {
      var _this2 = this;
      var showEvent = EventHandler.trigger(this._element, EVENT_SHOW);
      if (showEvent.defaultPrevented) {
        return;
      }
      this._clearTimeout();
      if (this._config.animation) {
        this._element.classList.add(CLASS_NAME_FADE);
      }
      var complete = function complete() {
        _this2._element.classList.remove(CLASS_NAME_SHOWING);
        EventHandler.trigger(_this2._element, EVENT_SHOWN);
        _this2._maybeScheduleHide();
      };
      this._element.classList.remove(CLASS_NAME_HIDE); // @deprecated
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_SHOW, CLASS_NAME_SHOWING);
      this._queueCallback(complete, this._element, this._config.animation);
    };
    _proto.hide = function hide() {
      var _this3 = this;
      if (!this.isShown()) {
        return;
      }
      var hideEvent = EventHandler.trigger(this._element, EVENT_HIDE);
      if (hideEvent.defaultPrevented) {
        return;
      }
      var complete = function complete() {
        _this3._element.classList.add(CLASS_NAME_HIDE); // @deprecated
        _this3._element.classList.remove(CLASS_NAME_SHOWING, CLASS_NAME_SHOW);
        EventHandler.trigger(_this3._element, EVENT_HIDDEN);
      };
      this._element.classList.add(CLASS_NAME_SHOWING);
      this._queueCallback(complete, this._element, this._config.animation);
    };
    _proto.dispose = function dispose() {
      this._clearTimeout();
      if (this.isShown()) {
        this._element.classList.remove(CLASS_NAME_SHOW);
      }
      _BaseComponent.prototype.dispose.call(this);
    };
    _proto.isShown = function isShown() {
      return this._element.classList.contains(CLASS_NAME_SHOW);
    }

    // Private
    ;
    _proto._maybeScheduleHide = function _maybeScheduleHide() {
      var _this4 = this;
      if (!this._config.autohide) {
        return;
      }
      if (this._hasMouseInteraction || this._hasKeyboardInteraction) {
        return;
      }
      this._timeout = setTimeout(function () {
        _this4.hide();
      }, this._config.delay);
    };
    _proto._onInteraction = function _onInteraction(event, isInteracting) {
      switch (event.type) {
        case 'mouseover':
        case 'mouseout':
          {
            this._hasMouseInteraction = isInteracting;
            break;
          }
        case 'focusin':
        case 'focusout':
          {
            this._hasKeyboardInteraction = isInteracting;
            break;
          }
      }
      if (isInteracting) {
        this._clearTimeout();
        return;
      }
      var nextElement = event.relatedTarget;
      if (this._element === nextElement || this._element.contains(nextElement)) {
        return;
      }
      this._maybeScheduleHide();
    };
    _proto._setListeners = function _setListeners() {
      var _this5 = this;
      EventHandler.on(this._element, EVENT_MOUSEOVER, function (event) {
        return _this5._onInteraction(event, true);
      });
      EventHandler.on(this._element, EVENT_MOUSEOUT, function (event) {
        return _this5._onInteraction(event, false);
      });
      EventHandler.on(this._element, EVENT_FOCUSIN, function (event) {
        return _this5._onInteraction(event, true);
      });
      EventHandler.on(this._element, EVENT_FOCUSOUT, function (event) {
        return _this5._onInteraction(event, false);
      });
    };
    _proto._clearTimeout = function _clearTimeout() {
      clearTimeout(this._timeout);
      this._timeout = null;
    }

    // Static
    ;
    Toast.jQueryInterface = function jQueryInterface(config) {
      return this.each(function () {
        var data = Toast.getOrCreateInstance(this, config);
        if (typeof config === 'string') {
          if (typeof data[config] === 'undefined') {
            throw new TypeError("No method named \"" + config + "\"");
          }
          data[config](this);
        }
      });
    };
    _createClass(Toast, null, [{
      key: "Default",
      get: function get() {
        return Default;
      }
    }, {
      key: "DefaultType",
      get: function get() {
        return DefaultType;
      }
    }, {
      key: "NAME",
      get: function get() {
        return NAME;
      }
    }]);
    return Toast;
  }(BaseComponent);
  /**
   * Data API implementation
   */
  enableDismissTrigger(Toast);

  /**
   * jQuery
   */

  defineJQueryPlugin(Toast);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap index.umd.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  const index_umd = {
    Alert: Alert,
    Button: Button,
    Carousel: Carousel,
    Collapse: Collapse,
    Dropdown: Dropdown,
    Modal: Modal,
    Offcanvas: Offcanvas,
    Popover: Popover,
    ScrollSpy: ScrollSpy,
    Tab: Tab,
    Toast: Toast,
    Tooltip: Tooltip
  };

  return index_umd;

}));
//# sourceMappingURL=bootstrap.js.map
