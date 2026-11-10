//#region \0rolldown/runtime.js
var e = Object.defineProperty, t = (e, t, n) => () => {
	if (n) throw n[0];
	try {
		return e && (t = e(e = 0)), t;
	} catch (e) {
		throw n = [e], e;
	}
}, n = (t, n) => {
	let r = {};
	for (var i in t) e(r, i, {
		get: t[i],
		enumerable: !0
	});
	return n || e(r, Symbol.toStringTag, { value: "Module" }), r;
}, r = "home-assistant", i = () => customElements.whenDefined(r), a, o, s, c, l, u, d, ee, te, ne = t((() => {
	a = globalThis, o = a.ShadowRoot && (a.ShadyCSS === void 0 || a.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, s = Symbol(), c = /* @__PURE__ */ new WeakMap(), l = class {
		constructor(e, t, n) {
			if (this._$cssResult$ = !0, n !== s) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
			this.cssText = e, this.t = t;
		}
		get styleSheet() {
			let e = this.o, t = this.t;
			if (o && e === void 0) {
				let n = t !== void 0 && t.length === 1;
				n && (e = c.get(t)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), n && c.set(t, e));
			}
			return e;
		}
		toString() {
			return this.cssText;
		}
	}, u = (e) => new l(typeof e == "string" ? e : e + "", void 0, s), d = (e, ...t) => {
		let n = e.length === 1 ? e[0] : t.reduce((t, n, r) => t + ((e) => {
			if (!0 === e._$cssResult$) return e.cssText;
			if (typeof e == "number") return e;
			throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
		})(n) + e[r + 1], e[0]);
		return new l(n, e, s);
	}, ee = (e, t) => {
		if (o) e.adoptedStyleSheets = t.map((e) => e instanceof CSSStyleSheet ? e : e.styleSheet);
		else for (let n of t) {
			let t = document.createElement("style"), r = a.litNonce;
			r !== void 0 && t.setAttribute("nonce", r), t.textContent = n.cssText, e.appendChild(t);
		}
	}, te = o ? (e) => e : (e) => e instanceof CSSStyleSheet ? ((e) => {
		let t = "";
		for (let n of e.cssRules) t += n.cssText;
		return u(t);
	})(e) : e;
})), re, ie, ae, oe, se, ce, le, ue, de, fe, f, pe, me, he, p, ge = t((() => {
	ne(), {is: re, defineProperty: ie, getOwnPropertyDescriptor: ae, getOwnPropertyNames: oe, getOwnPropertySymbols: se, getPrototypeOf: ce} = Object, le = globalThis, ue = le.trustedTypes, de = ue ? ue.emptyScript : "", fe = le.reactiveElementPolyfillSupport, f = (e, t) => e, pe = {
		toAttribute(e, t) {
			switch (t) {
				case Boolean:
					e = e ? de : null;
					break;
				case Object:
				case Array: e = e == null ? e : JSON.stringify(e);
			}
			return e;
		},
		fromAttribute(e, t) {
			let n = e;
			switch (t) {
				case Boolean:
					n = e !== null;
					break;
				case Number:
					n = e === null ? null : Number(e);
					break;
				case Object:
				case Array: try {
					n = JSON.parse(e);
				} catch {
					n = null;
				}
			}
			return n;
		}
	}, me = (e, t) => !re(e, t), he = {
		attribute: !0,
		type: String,
		converter: pe,
		reflect: !1,
		useDefault: !1,
		hasChanged: me
	}, Symbol.metadata ??= Symbol("metadata"), le.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap(), p = class extends HTMLElement {
		static addInitializer(e) {
			this._$Ei(), (this.l ??= []).push(e);
		}
		static get observedAttributes() {
			return this.finalize(), this._$Eh && [...this._$Eh.keys()];
		}
		static createProperty(e, t = he) {
			if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
				let n = Symbol(), r = this.getPropertyDescriptor(e, n, t);
				r !== void 0 && ie(this.prototype, e, r);
			}
		}
		static getPropertyDescriptor(e, t, n) {
			let { get: r, set: i } = ae(this.prototype, e) ?? {
				get() {
					return this[t];
				},
				set(e) {
					this[t] = e;
				}
			};
			return {
				get: r,
				set(t) {
					let a = r?.call(this);
					i?.call(this, t), this.requestUpdate(e, a, n);
				},
				configurable: !0,
				enumerable: !0
			};
		}
		static getPropertyOptions(e) {
			return this.elementProperties.get(e) ?? he;
		}
		static _$Ei() {
			if (this.hasOwnProperty(f("elementProperties"))) return;
			let e = ce(this);
			e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
		}
		static finalize() {
			if (this.hasOwnProperty(f("finalized"))) return;
			if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(f("properties"))) {
				let e = this.properties, t = [...oe(e), ...se(e)];
				for (let n of t) this.createProperty(n, e[n]);
			}
			let e = this[Symbol.metadata];
			if (e !== null) {
				let t = litPropertyMetadata.get(e);
				if (t !== void 0) for (let [e, n] of t) this.elementProperties.set(e, n);
			}
			this._$Eh = /* @__PURE__ */ new Map();
			for (let [e, t] of this.elementProperties) {
				let n = this._$Eu(e, t);
				n !== void 0 && this._$Eh.set(n, e);
			}
			this.elementStyles = this.finalizeStyles(this.styles);
		}
		static finalizeStyles(e) {
			let t = [];
			if (Array.isArray(e)) {
				let n = new Set(e.flat(1 / 0).reverse());
				for (let e of n) t.unshift(te(e));
			} else e !== void 0 && t.push(te(e));
			return t;
		}
		static _$Eu(e, t) {
			let n = t.attribute;
			return !1 === n ? void 0 : typeof n == "string" ? n : typeof e == "string" ? e.toLowerCase() : void 0;
		}
		constructor() {
			super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
		}
		_$Ev() {
			this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((e) => e(this));
		}
		addController(e) {
			(this._$EO ??= /* @__PURE__ */ new Set()).add(e), this.renderRoot !== void 0 && this.isConnected && e.hostConnected?.();
		}
		removeController(e) {
			this._$EO?.delete(e);
		}
		_$E_() {
			let e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
			for (let n of t.keys()) this.hasOwnProperty(n) && (e.set(n, this[n]), delete this[n]);
			e.size > 0 && (this._$Ep = e);
		}
		createRenderRoot() {
			let e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
			return ee(e, this.constructor.elementStyles), e;
		}
		connectedCallback() {
			this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(!0), this._$EO?.forEach((e) => e.hostConnected?.());
		}
		enableUpdating(e) {}
		disconnectedCallback() {
			this._$EO?.forEach((e) => e.hostDisconnected?.());
		}
		attributeChangedCallback(e, t, n) {
			this._$AK(e, n);
		}
		_$ET(e, t) {
			let n = this.constructor.elementProperties.get(e), r = this.constructor._$Eu(e, n);
			if (r !== void 0 && !0 === n.reflect) {
				let i = (n.converter?.toAttribute === void 0 ? pe : n.converter).toAttribute(t, n.type);
				this._$Em = e, i == null ? this.removeAttribute(r) : this.setAttribute(r, i), this._$Em = null;
			}
		}
		_$AK(e, t) {
			let n = this.constructor, r = n._$Eh.get(e);
			if (r !== void 0 && this._$Em !== r) {
				let e = n.getPropertyOptions(r), i = typeof e.converter == "function" ? { fromAttribute: e.converter } : e.converter?.fromAttribute === void 0 ? pe : e.converter;
				this._$Em = r;
				let a = i.fromAttribute(t, e.type);
				this[r] = a ?? this._$Ej?.get(r) ?? a, this._$Em = null;
			}
		}
		requestUpdate(e, t, n, r = !1, i) {
			if (e !== void 0) {
				let a = this.constructor;
				if (!1 === r && (i = this[e]), n ??= a.getPropertyOptions(e), !((n.hasChanged ?? me)(i, t) || n.useDefault && n.reflect && i === this._$Ej?.get(e) && !this.hasAttribute(a._$Eu(e, n)))) return;
				this.C(e, t, n);
			}
			!1 === this.isUpdatePending && (this._$ES = this._$EP());
		}
		C(e, t, { useDefault: n, reflect: r, wrapped: i }, a) {
			n && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(e) && (this._$Ej.set(e, a ?? t ?? this[e]), !0 !== i || a !== void 0) || (this._$AL.has(e) || (this.hasUpdated || n || (t = void 0), this._$AL.set(e, t)), !0 === r && this._$Em !== e && (this._$Eq ??= /* @__PURE__ */ new Set()).add(e));
		}
		async _$EP() {
			this.isUpdatePending = !0;
			try {
				await this._$ES;
			} catch (e) {
				Promise.reject(e);
			}
			let e = this.scheduleUpdate();
			return e != null && await e, !this.isUpdatePending;
		}
		scheduleUpdate() {
			return this.performUpdate();
		}
		performUpdate() {
			if (!this.isUpdatePending) return;
			if (!this.hasUpdated) {
				if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
					for (let [e, t] of this._$Ep) this[e] = t;
					this._$Ep = void 0;
				}
				let e = this.constructor.elementProperties;
				if (e.size > 0) for (let [t, n] of e) {
					let { wrapped: e } = n, r = this[t];
					!0 !== e || this._$AL.has(t) || r === void 0 || this.C(t, void 0, n, r);
				}
			}
			let e = !1, t = this._$AL;
			try {
				e = this.shouldUpdate(t), e ? (this.willUpdate(t), this._$EO?.forEach((e) => e.hostUpdate?.()), this.update(t)) : this._$EM();
			} catch (t) {
				throw e = !1, this._$EM(), t;
			}
			e && this._$AE(t);
		}
		willUpdate(e) {}
		_$AE(e) {
			this._$EO?.forEach((e) => e.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
		}
		_$EM() {
			this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
		}
		get updateComplete() {
			return this.getUpdateComplete();
		}
		getUpdateComplete() {
			return this._$ES;
		}
		shouldUpdate(e) {
			return !0;
		}
		update(e) {
			this._$Eq &&= this._$Eq.forEach((e) => this._$ET(e, this[e])), this._$EM();
		}
		updated(e) {}
		firstUpdated(e) {}
	}, p.elementStyles = [], p.shadowRootOptions = { mode: "open" }, p[f("elementProperties")] = /* @__PURE__ */ new Map(), p[f("finalized")] = /* @__PURE__ */ new Map(), fe?.({ ReactiveElement: p }), (le.reactiveElementVersions ??= []).push("2.1.2");
}));
//#endregion
//#region node_modules/lit-html/lit-html.js
function _e(e, t) {
	if (!Te(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
	return xe === void 0 ? t : xe.createHTML(t);
}
function m(e, t, n = e, r) {
	if (t === C) return t;
	let i = r === void 0 ? n._$Cl : n._$Co?.[r], a = v(t) ? void 0 : t._$litDirective$;
	return i?.constructor !== a && (i?._$AO?.(!1), a === void 0 ? i = void 0 : (i = new a(e), i._$AT(e, n, r)), r === void 0 ? n._$Cl = i : (n._$Co ??= [])[r] = i), i !== void 0 && (t = m(e, i._$AS(e, t.values), i, r)), t;
}
var ve, ye, be, xe, Se, h, Ce, we, g, _, v, Te, Ee, De, y, Oe, ke, b, Ae, je, Me, Ne, x, S, C, w, Pe, T, Fe, Ie, Le, Re, ze, Be, Ve, He, Ue, We, Ge, Ke = t((() => {
	ve = globalThis, ye = (e) => e, be = ve.trustedTypes, xe = be ? be.createPolicy("lit-html", { createHTML: (e) => e }) : void 0, Se = "$lit$", h = `lit$${Math.random().toFixed(9).slice(2)}$`, Ce = "?" + h, we = `<${Ce}>`, g = document, _ = () => g.createComment(""), v = (e) => e === null || typeof e != "object" && typeof e != "function", Te = Array.isArray, Ee = (e) => Te(e) || typeof e?.[Symbol.iterator] == "function", De = "[ 	\n\f\r]", y = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, Oe = /-->/g, ke = />/g, b = RegExp(`>|${De}(?:([^\\s"'>=/]+)(${De}*=${De}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"), Ae = /'/g, je = /"/g, Me = /^(?:script|style|textarea|title)$/i, Ne = (e) => (t, ...n) => ({
		_$litType$: e,
		strings: t,
		values: n
	}), x = Ne(1), S = Ne(2), Ne(3), C = Symbol.for("lit-noChange"), w = Symbol.for("lit-nothing"), Pe = /* @__PURE__ */ new WeakMap(), T = g.createTreeWalker(g, 129), Fe = (e, t) => {
		let n = e.length - 1, r = [], i, a = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", o = y;
		for (let t = 0; t < n; t++) {
			let n = e[t], s, c, l = -1, u = 0;
			for (; u < n.length && (o.lastIndex = u, c = o.exec(n), c !== null);) u = o.lastIndex, o === y ? c[1] === "!--" ? o = Oe : c[1] === void 0 ? c[2] === void 0 ? c[3] !== void 0 && (o = b) : (Me.test(c[2]) && (i = RegExp("</" + c[2], "g")), o = b) : o = ke : o === b ? c[0] === ">" ? (o = i ?? y, l = -1) : c[1] === void 0 ? l = -2 : (l = o.lastIndex - c[2].length, s = c[1], o = c[3] === void 0 ? b : c[3] === "\"" ? je : Ae) : o === je || o === Ae ? o = b : o === Oe || o === ke ? o = y : (o = b, i = void 0);
			let d = o === b && e[t + 1].startsWith("/>") ? " " : "";
			a += o === y ? n + we : l >= 0 ? (r.push(s), n.slice(0, l) + Se + n.slice(l) + h + d) : n + h + (l === -2 ? t : d);
		}
		return [_e(e, a + (e[n] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), r];
	}, Ie = class e {
		constructor({ strings: t, _$litType$: n }, r) {
			let i;
			this.parts = [];
			let a = 0, o = 0, s = t.length - 1, c = this.parts, [l, u] = Fe(t, n);
			if (this.el = e.createElement(l, r), T.currentNode = this.el.content, n === 2 || n === 3) {
				let e = this.el.content.firstChild;
				e.replaceWith(...e.childNodes);
			}
			for (; (i = T.nextNode()) !== null && c.length < s;) {
				if (i.nodeType === 1) {
					if (i.hasAttributes()) for (let e of i.getAttributeNames()) if (e.endsWith(Se)) {
						let t = u[o++], n = i.getAttribute(e).split(h), r = /([.?@])?(.*)/.exec(t);
						c.push({
							type: 1,
							index: a,
							name: r[2],
							strings: n,
							ctor: r[1] === "." ? Be : r[1] === "?" ? Ve : r[1] === "@" ? He : ze
						}), i.removeAttribute(e);
					} else e.startsWith(h) && (c.push({
						type: 6,
						index: a
					}), i.removeAttribute(e));
					if (Me.test(i.tagName)) {
						let e = i.textContent.split(h), t = e.length - 1;
						if (t > 0) {
							i.textContent = be ? be.emptyScript : "";
							for (let n = 0; n < t; n++) i.append(e[n], _()), T.nextNode(), c.push({
								type: 2,
								index: ++a
							});
							i.append(e[t], _());
						}
					}
				} else if (i.nodeType === 8) {
					if (i.data === Ce) c.push({
						type: 2,
						index: a
					});
					else {
						let e = -1;
						for (; (e = i.data.indexOf(h, e + 1)) !== -1;) c.push({
							type: 7,
							index: a
						}), e += h.length - 1;
					}
				}
				a++;
			}
		}
		static createElement(e, t) {
			let n = g.createElement("template");
			return n.innerHTML = e, n;
		}
	}, Le = class {
		constructor(e, t) {
			this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
		}
		get parentNode() {
			return this._$AM.parentNode;
		}
		get _$AU() {
			return this._$AM._$AU;
		}
		u(e) {
			let { el: { content: t }, parts: n } = this._$AD, r = (e?.creationScope ?? g).importNode(t, !0);
			T.currentNode = r;
			let i = T.nextNode(), a = 0, o = 0, s = n[0];
			for (; s !== void 0;) {
				if (a === s.index) {
					let t;
					s.type === 2 ? t = new Re(i, i.nextSibling, this, e) : s.type === 1 ? t = new s.ctor(i, s.name, s.strings, this, e) : s.type === 6 && (t = new Ue(i, this, e)), this._$AV.push(t), s = n[++o];
				}
				a !== s?.index && (i = T.nextNode(), a++);
			}
			return T.currentNode = g, r;
		}
		p(e) {
			let t = 0;
			for (let n of this._$AV) n !== void 0 && (n.strings === void 0 ? n._$AI(e[t]) : (n._$AI(e, n, t), t += n.strings.length - 2)), t++;
		}
	}, Re = class e {
		get _$AU() {
			return this._$AM?._$AU ?? this._$Cv;
		}
		constructor(e, t, n, r) {
			this.type = 2, this._$AH = w, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = n, this.options = r, this._$Cv = r?.isConnected ?? !0;
		}
		get parentNode() {
			let e = this._$AA.parentNode, t = this._$AM;
			return t !== void 0 && e?.nodeType === 11 && (e = t.parentNode), e;
		}
		get startNode() {
			return this._$AA;
		}
		get endNode() {
			return this._$AB;
		}
		_$AI(e, t = this) {
			e = m(this, e, t), v(e) ? e === w || e == null || e === "" ? (this._$AH !== w && this._$AR(), this._$AH = w) : e !== this._$AH && e !== C && this._(e) : e._$litType$ === void 0 ? e.nodeType === void 0 ? Ee(e) ? this.k(e) : this._(e) : this.T(e) : this.$(e);
		}
		O(e) {
			return this._$AA.parentNode.insertBefore(e, this._$AB);
		}
		T(e) {
			this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
		}
		_(e) {
			this._$AH !== w && v(this._$AH) ? this._$AA.nextSibling.data = e : this.T(g.createTextNode(e)), this._$AH = e;
		}
		$(e) {
			let { values: t, _$litType$: n } = e, r = typeof n == "number" ? this._$AC(e) : (n.el === void 0 && (n.el = Ie.createElement(_e(n.h, n.h[0]), this.options)), n);
			if (this._$AH?._$AD === r) this._$AH.p(t);
			else {
				let e = new Le(r, this), n = e.u(this.options);
				e.p(t), this.T(n), this._$AH = e;
			}
		}
		_$AC(e) {
			let t = Pe.get(e.strings);
			return t === void 0 && Pe.set(e.strings, t = new Ie(e)), t;
		}
		k(t) {
			Te(this._$AH) || (this._$AH = [], this._$AR());
			let n = this._$AH, r, i = 0;
			for (let a of t) i === n.length ? n.push(r = new e(this.O(_()), this.O(_()), this, this.options)) : r = n[i], r._$AI(a), i++;
			i < n.length && (this._$AR(r && r._$AB.nextSibling, i), n.length = i);
		}
		_$AR(e = this._$AA.nextSibling, t) {
			for (this._$AP?.(!1, !0, t); e !== this._$AB;) {
				let t = ye(e).nextSibling;
				ye(e).remove(), e = t;
			}
		}
		setConnected(e) {
			this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
		}
	}, ze = class {
		get tagName() {
			return this.element.tagName;
		}
		get _$AU() {
			return this._$AM._$AU;
		}
		constructor(e, t, n, r, i) {
			this.type = 1, this._$AH = w, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = i, n.length > 2 || n[0] !== "" || n[1] !== "" ? (this._$AH = Array(n.length - 1).fill(/* @__PURE__ */ new String()), this.strings = n) : this._$AH = w;
		}
		_$AI(e, t = this, n, r) {
			let i = this.strings, a = !1;
			if (i === void 0) e = m(this, e, t, 0), a = !v(e) || e !== this._$AH && e !== C, a && (this._$AH = e);
			else {
				let r = e, o, s;
				for (e = i[0], o = 0; o < i.length - 1; o++) s = m(this, r[n + o], t, o), s === C && (s = this._$AH[o]), a ||= !v(s) || s !== this._$AH[o], s === w ? e = w : e !== w && (e += (s ?? "") + i[o + 1]), this._$AH[o] = s;
			}
			a && !r && this.j(e);
		}
		j(e) {
			e === w ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
		}
	}, Be = class extends ze {
		constructor() {
			super(...arguments), this.type = 3;
		}
		j(e) {
			this.element[this.name] = e === w ? void 0 : e;
		}
	}, Ve = class extends ze {
		constructor() {
			super(...arguments), this.type = 4;
		}
		j(e) {
			this.element.toggleAttribute(this.name, !!e && e !== w);
		}
	}, He = class extends ze {
		constructor(e, t, n, r, i) {
			super(e, t, n, r, i), this.type = 5;
		}
		_$AI(e, t = this) {
			if ((e = m(this, e, t, 0) ?? w) === C) return;
			let n = this._$AH, r = e === w && n !== w || e.capture !== n.capture || e.once !== n.once || e.passive !== n.passive, i = e !== w && (n === w || r);
			r && this.element.removeEventListener(this.name, this, n), i && this.element.addEventListener(this.name, this, e), this._$AH = e;
		}
		handleEvent(e) {
			typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
		}
	}, Ue = class {
		constructor(e, t, n) {
			this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = n;
		}
		get _$AU() {
			return this._$AM._$AU;
		}
		_$AI(e) {
			m(this, e);
		}
	}, We = ve.litHtmlPolyfillSupport, We?.(Ie, Re), (ve.litHtmlVersions ??= []).push("3.3.3"), Ge = (e, t, n) => {
		let r = n?.renderBefore ?? t, i = r._$litPart$;
		if (i === void 0) {
			let e = n?.renderBefore ?? null;
			r._$litPart$ = i = new Re(t.insertBefore(_(), e), e, void 0, n ?? {});
		}
		return i._$AI(e), i;
	};
})), qe, E, Je, Ye = t((() => {
	ge(), ge(), Ke(), Ke(), qe = globalThis, E = class extends p {
		constructor() {
			super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
		}
		createRenderRoot() {
			let e = super.createRenderRoot();
			return this.renderOptions.renderBefore ??= e.firstChild, e;
		}
		update(e) {
			let t = this.render();
			this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Ge(t, this.renderRoot, this.renderOptions);
		}
		connectedCallback() {
			super.connectedCallback(), this._$Do?.setConnected(!0);
		}
		disconnectedCallback() {
			super.disconnectedCallback(), this._$Do?.setConnected(!1);
		}
		render() {
			return C;
		}
	}, E._$litElement$ = !0, E.finalized = !0, qe.litElementHydrateSupport?.({ LitElement: E }), Je = qe.litElementPolyfillSupport, Je?.({ LitElement: E }), (qe.litElementVersions ??= []).push("4.2.2");
})), Xe = t((() => {})), D = t((() => {
	ge(), Ke(), Ye(), Xe();
})), Ze, Qe, $e, et = t((() => {
	Ze = {
		ATTRIBUTE: 1,
		CHILD: 2,
		PROPERTY: 3,
		BOOLEAN_ATTRIBUTE: 4,
		EVENT: 5,
		ELEMENT: 6
	}, Qe = (e) => (...t) => ({
		_$litDirective$: e,
		values: t
	}), $e = class {
		constructor(e) {}
		get _$AU() {
			return this._$AM._$AU;
		}
		_$AT(e, t, n) {
			this._$Ct = e, this._$AM = t, this._$Ci = n;
		}
		_$AS(e, t) {
			return this.update(e, t);
		}
		update(e, t) {
			return this.render(...t);
		}
	};
})), tt, nt, rt, it = t((() => {
	Ke(), et(), tt = "important", nt = " !" + tt, rt = Qe(class extends $e {
		constructor(e) {
			if (super(e), e.type !== Ze.ATTRIBUTE || e.name !== "style" || e.strings?.length > 2) throw Error("The `styleMap` directive must be used in the `style` attribute and must be the only part in the attribute.");
		}
		render(e) {
			return Object.keys(e).reduce((t, n) => {
				let r = e[n];
				return r == null ? t : t + `${n = n.includes("-") ? n : n.replace(/(?:^(webkit|moz|ms|o)|)(?=[A-Z])/g, "-$&").toLowerCase()}:${r};`;
			}, "");
		}
		update(e, [t]) {
			let { style: n } = e.element;
			if (this.ft === void 0) return this.ft = new Set(Object.keys(t)), this.render(t);
			for (let e of this.ft) t[e] ?? (this.ft.delete(e), e.includes("-") ? n.removeProperty(e) : n[e] = null);
			for (let e in t) {
				let r = t[e];
				if (r != null) {
					this.ft.add(e);
					let t = typeof r == "string" && r.endsWith(nt);
					e.includes("-") || t ? n.setProperty(e, t ? r.slice(0, -11) : r, t ? tt : "") : n[e] = r;
				}
			}
			return C;
		}
	});
})), at = t((() => {
	it();
})), ot, st, ct, lt, ut, dt = t((() => {
	ot = "hass-action", st = "/config/integrations/integration/saj_local", ct = (e) => `/config/devices/device/${e}`, lt = ({ host: e, entityId: t }) => {
		e.dispatchEvent(new CustomEvent(ot, {
			bubbles: !0,
			composed: !0,
			detail: {
				action: "tap",
				config: {
					entity: t,
					tap_action: { action: "more-info" }
				}
			}
		}));
	}, ut = ({ host: e, path: t }) => {
		e.dispatchEvent(new CustomEvent(ot, {
			bubbles: !0,
			composed: !0,
			detail: {
				action: "tap",
				config: { tap_action: {
					action: "navigate",
					navigation_path: t
				} }
			}
		}));
	};
})), ft, pt, mt, ht, gt, _t, vt, yt, bt, xt, St, Ct, wt, Tt, Et, Dt, Ot, kt, At, jt, Mt, Nt, Pt, Ft, It, Lt, Rt, zt, Bt, Vt, Ht, Ut, Wt, Gt, Kt, qt, Jt, Yt, Xt, Zt, Qt, $t, en, tn, nn, rn, an, on, sn, cn, ln, un, dn, fn, pn, mn, hn, gn, _n, vn, yn, bn, xn, Sn, Cn, wn, Tn, En, Dn, On, kn, An, jn, Mn, Nn, Pn, Fn, In, Ln, Rn, zn, Bn, Vn, Hn, Un, Wn, Gn = t((() => {
	ft = "SAJ-Local-System auswählen", pt = "SAJ-Local-Status", mt = "Betriebszustand und Anzahl der aktiven Fehler eines SAJ-Local-Systems", ht = "Antwortet nicht", gt = "Nicht verfügbar", _t = "In Arbeit", vt = "Drücken", yt = "Wochenzeitleiste", bt = "Die Steuerung ist für dieses System ausgeschaltet", xt = "Einstellungen öffnen", St = "Noch nichts anzuzeigen", Ct = "Aktiviere die Entitäten ({kind}) auf der Geräteseite des Systems, um sie hier anzuzeigen.", wt = "Geräteseite öffnen", Tt = "Messwerte", Et = "Konfiguration", Dt = "Zeitplan", Ot = "Solar", kt = "Batterie", At = "Netz", jt = "Haus", Mt = "Wechselrichter", Nt = "Wallbox", Pt = "Notstromlast", Ft = "Zähler B", It = "Laden", Lt = "Entladen", Rt = "Netzbezug", zt = "Einspeisung", Bt = "Inaktiv", Vt = "Keine Fehler", Ht = "Fehler", Ut = "Steuerung", Wt = "Pack {number}", Gt = "{count} Fehler", Kt = "{count} Fehler", qt = "Keine aktiven Fehler", Jt = "Fehler quittieren", Yt = "Register und Bit stehen im Diagnosedownload", Xt = "Steuerung zugelassen", Zt = "Steuerung aus", Qt = "Dieses System hat keine Batterie", $t = "Modus", en = "Läuft gerade", tn = "Lade- und Entladezeitfenster laufen nur im Modus Zeitsteuerung", nn = "Zeitfenster {number}", rn = "{count} Zeitfenster hat deaktivierte Entitäten", an = "{count} Zeitfenster haben deaktivierte Entitäten", on = "Wochentage", sn = "Positiv entlädt, negativ lädt", cn = "Positiv speist ein, negativ bezieht", ln = "Positiv gibt ab, negativ nimmt auf", un = "Modus", dn = "Batterie", fn = "Netz", pn = "Leistungssteuerung", mn = "Wallbox", hn = "Gerät", gn = "System", _n = "Solar-Strings anzeigen", vn = "Optionale Ausstattung anzeigen", yn = "Umfang", bn = "Dieses System", xn = "Parallelsystem", Sn = "Energie von heute anzeigen", Cn = "Gruppen ohne Fehler anzeigen", wn = "Batteriepacks anzeigen", Tn = "Abschnitte", En = "Zeitfensterarten", Dn = "Laden", On = "Entladen", kn = "Wallbox", An = "Wochenzeitleiste anzeigen", jn = "SAJ-Local-Energiefluss", Mn = "Live-Leistung zwischen Solar, Batterie, Netz, Haus und der optionalen Ausstattung", Nn = "SAJ-Local-Status", Pn = "Betriebszustand, Modus, wichtige Messwerte, Energie von heute, Fehler und ob die Steuerung zugelassen ist", Fn = "SAJ-Local-Fehler", In = "Aktive Fehler je Ausstattungsteil, mit Fehler quittieren", Ln = "SAJ-Local-Batterie", Rn = "Ladezustand mit Reserve und Grenzwerten, Batteriewerte und eine Zeile pro Pack", zn = "SAJ-Local-Steuerung", Bn = "Die gemeinsamen Bedienelemente des Systems", Vn = "SAJ-Local-Zeitplan", Hn = "Lade-, Entlade- und Wallbox-Zeitfenster mit einer Wochenzeitleiste", Un = "SAJ-Local-Wochentage", Wn = {
		choose_system: ft,
		badge_name: pt,
		badge_description: mt,
		not_answering: ht,
		unavailable: gt,
		busy: _t,
		press: vt,
		week_timeline: yt,
		locked_message: bt,
		open_settings: xt,
		empty_title: St,
		empty_enable: Ct,
		open_device_page: wt,
		entity_kind_reading: Tt,
		entity_kind_configuration: Et,
		entity_kind_schedule: Dt,
		solar: Ot,
		battery: kt,
		grid: At,
		home: jt,
		inverter: Mt,
		ev_charger: Nt,
		backup_load: Pt,
		meter_b: Ft,
		charging: It,
		discharging: Lt,
		importing: Rt,
		exporting: zt,
		idle: Bt,
		no_faults: Vt,
		faults: Ht,
		changes: Ut,
		battery_pack: Wt,
		faults_count_one: Gt,
		faults_count_other: Kt,
		no_active_faults: qt,
		clear_fault: Jt,
		see_diagnostics: Yt,
		changes_allowed: Xt,
		changes_off: Zt,
		no_battery: Qt,
		mode: $t,
		mode_running_now: en,
		time_of_use_notice: tn,
		slot_number: nn,
		slots_left_out_one: rn,
		slots_left_out_other: an,
		weekdays: on,
		sign_battery: sn,
		sign_grid: cn,
		sign_inverter: ln,
		section_mode: un,
		section_battery: dn,
		section_grid: fn,
		section_power_control: pn,
		section_ev_charger: mn,
		section_device: hn,
		option_device: gn,
		option_show_strings: _n,
		option_show_optional_equipment: vn,
		option_scope: yn,
		option_scope_system: bn,
		option_scope_parallel: xn,
		option_show_energy: Sn,
		option_show_groups_without_faults: Cn,
		option_show_packs: wn,
		option_sections: Tn,
		option_slot_kinds: En,
		option_kind_charge: Dn,
		option_kind_discharge: On,
		option_kind_ev_charger: kn,
		option_show_timeline: An,
		power_flow_card_name: jn,
		power_flow_card_description: Mn,
		status_card_name: Nn,
		status_card_description: Pn,
		faults_card_name: Fn,
		faults_card_description: In,
		battery_card_name: Ln,
		battery_card_description: Rn,
		controls_card_name: zn,
		controls_card_description: Bn,
		schedule_card_name: Vn,
		schedule_card_description: Hn,
		weekdays_feature_name: Un
	};
})), Kn, qn, Jn, Yn, Xn, Zn, Qn, $n, er, tr, nr, rr, ir, ar, or, sr, cr, lr, ur, dr, fr, pr, mr, hr, gr, _r, vr, yr, br, xr, Sr, Cr, wr, Tr, Er, Dr, Or, kr, Ar, jr, Mr, Nr, Pr, Fr, Ir, Lr, Rr, zr, Br, Vr, Hr, Ur, Wr, Gr, Kr, qr, Jr, Yr, Xr, Zr, Qr, $r, ei, ti, ni, ri, ii, ai, oi, si, ci, li, ui, di, fi, pi, mi, hi, gi, _i, vi, yi, bi, xi, Si, Ci, wi = t((() => {
	Kn = "Choose a SAJ Local system", qn = "SAJ Local status", Jn = "Operating state and active fault count of a SAJ Local system", Yn = "Not answering", Xn = "Unavailable", Zn = "Working", Qn = "Press", $n = "Week timeline", er = "Control is off for this system", tr = "Open settings", nr = "Nothing to show yet", rr = "Enable {kind} entities on the system's device page to show them here.", ir = "Open device page", ar = "reading", or = "configuration", sr = "schedule", cr = "Solar", lr = "Battery", ur = "Grid", dr = "Home", fr = "Inverter", pr = "EV charger", mr = "Backup load", hr = "Meter B", gr = "Charging", _r = "Discharging", vr = "Importing", yr = "Exporting", br = "Idle", xr = "No faults", Sr = "Faults", Cr = "Control", wr = "Pack {number}", Tr = "{count} fault", Er = "{count} faults", Dr = "No active faults", Or = "Clear fault", kr = "See the diagnostics download for the register and bit", Ar = "Control allowed", jr = "Control off", Mr = "This system has no battery", Nr = "Mode", Pr = "Running now", Fr = "Charge and discharge slots only run in time-of-use mode", Ir = "Slot {number}", Lr = "{count} slot has disabled entities", Rr = "{count} slots have disabled entities", zr = "Days of the week", Br = "Positive discharges, negative charges", Vr = "Positive exports, negative imports", Hr = "Positive puts out, negative takes in", Ur = "Mode", Wr = "Battery", Gr = "Grid", Kr = "Power control", qr = "EV charger", Jr = "Device", Yr = "System", Xr = "Show solar strings", Zr = "Show optional equipment", Qr = "Scope", $r = "This system", ei = "Parallel system", ti = "Show today's energy", ni = "Show groups without faults", ri = "Show battery packs", ii = "Sections", ai = "Slot kinds", oi = "Charge", si = "Discharge", ci = "EV charger", li = "Show week timeline", ui = "SAJ Local power flow", di = "Live power between solar, battery, grid, home and the optional equipment", fi = "SAJ Local status", pi = "Operating state, mode, key readings, today's energy, faults and whether control is allowed", mi = "SAJ Local faults", hi = "Active faults per piece of equipment, with clear fault", gi = "SAJ Local battery", _i = "State of charge with reserve and limits, battery readings and one row per pack", vi = "SAJ Local controls", yi = "The shared controls the system offers", bi = "SAJ Local schedule", xi = "Charge, discharge and EV charger slots with a week timeline", Si = "SAJ Local weekdays", Ci = {
		choose_system: Kn,
		badge_name: qn,
		badge_description: Jn,
		not_answering: Yn,
		unavailable: Xn,
		busy: Zn,
		press: Qn,
		week_timeline: $n,
		locked_message: er,
		open_settings: tr,
		empty_title: nr,
		empty_enable: rr,
		open_device_page: ir,
		entity_kind_reading: ar,
		entity_kind_configuration: or,
		entity_kind_schedule: sr,
		solar: cr,
		battery: lr,
		grid: ur,
		home: dr,
		inverter: fr,
		ev_charger: pr,
		backup_load: mr,
		meter_b: hr,
		charging: gr,
		discharging: _r,
		importing: vr,
		exporting: yr,
		idle: br,
		no_faults: xr,
		faults: Sr,
		changes: Cr,
		battery_pack: wr,
		faults_count_one: Tr,
		faults_count_other: Er,
		no_active_faults: Dr,
		clear_fault: Or,
		see_diagnostics: kr,
		changes_allowed: Ar,
		changes_off: jr,
		no_battery: Mr,
		mode: Nr,
		mode_running_now: Pr,
		time_of_use_notice: Fr,
		slot_number: Ir,
		slots_left_out_one: Lr,
		slots_left_out_other: Rr,
		weekdays: zr,
		sign_battery: Br,
		sign_grid: Vr,
		sign_inverter: Hr,
		section_mode: Ur,
		section_battery: Wr,
		section_grid: Gr,
		section_power_control: Kr,
		section_ev_charger: qr,
		section_device: Jr,
		option_device: Yr,
		option_show_strings: Xr,
		option_show_optional_equipment: Zr,
		option_scope: Qr,
		option_scope_system: $r,
		option_scope_parallel: ei,
		option_show_energy: ti,
		option_show_groups_without_faults: ni,
		option_show_packs: ri,
		option_sections: ii,
		option_slot_kinds: ai,
		option_kind_charge: oi,
		option_kind_discharge: si,
		option_kind_ev_charger: ci,
		option_show_timeline: li,
		power_flow_card_name: ui,
		power_flow_card_description: di,
		status_card_name: fi,
		status_card_description: pi,
		faults_card_name: mi,
		faults_card_description: hi,
		battery_card_name: gi,
		battery_card_description: _i,
		controls_card_name: vi,
		controls_card_description: yi,
		schedule_card_name: bi,
		schedule_card_description: xi,
		weekdays_feature_name: Si
	};
})), Ti, Ei, Di, Oi, ki, Ai, ji, Mi, Ni, Pi, Fi, Ii, Li, Ri, zi, Bi, Vi, Hi, Ui, Wi, Gi, Ki, qi, Ji, Yi, Xi, Zi, Qi, $i, ea, ta, na, ra, ia, aa, oa, sa, ca, la, ua, da, fa, pa, ma, ha, ga, _a, va, ya, ba, xa, Sa, Ca, wa, Ta, Ea, Da, Oa, ka, Aa, ja, Ma, Na, Pa, Fa, Ia, La, Ra, za, Ba, Va, Ha, Ua, Wa, Ga, Ka, qa, Ja, Ya, Xa, Za, Qa, $a, eo, to, no, ro = t((() => {
	Ti = "Elige un sistema SAJ Local", Ei = "Estado de SAJ Local", Di = "Estado de funcionamiento y número de fallos activos de un sistema SAJ Local", Oi = "Sin respuesta", ki = "No disponible", Ai = "Procesando", ji = "Pulsar", Mi = "Línea de tiempo semanal", Ni = "El control está desactivado para este sistema", Pi = "Abrir ajustes", Fi = "Nada que mostrar todavía", Ii = "Habilita las entidades de {kind} en la página del dispositivo del sistema para mostrarlas aquí.", Li = "Abrir la página del dispositivo", Ri = "lectura", zi = "configuración", Bi = "programación", Vi = "Solar", Hi = "Batería", Ui = "Casa", Wi = "Inversor", Gi = "Cargador de VE", Ki = "Carga de respaldo", qi = "Contador B", Ji = "Cargando", Yi = "Descargando", Xi = "Importando", Zi = "Exportando", Qi = "Inactivo", $i = "Sin fallos", ea = "Fallos", ta = "Control", na = "Módulo {number}", ra = "{count} fallo", ia = "{count} de fallos", aa = "{count} fallos", oa = "Sin fallos activos", sa = "Borrar fallo", ca = "Consulta la descarga de diagnósticos para ver el registro Modbus y el bit", la = "Control permitido", ua = "Control desactivado", da = "Este sistema no tiene batería", fa = "Modo", pa = "En marcha ahora", ma = "Las franjas de carga y descarga solo funcionan en el modo horario programado", ha = "Franja {number}", ga = "{count} franja tiene entidades deshabilitadas", _a = "{count} de franjas tienen entidades deshabilitadas", va = "{count} franjas tienen entidades deshabilitadas", ya = "Días de la semana", ba = "Positivo descarga, negativo carga", xa = "Positivo exporta, negativo importa", Sa = "Positivo entrega, negativo absorbe", Ca = "Modo", wa = "Batería", Ta = "Control de potencia", Ea = "Cargador de VE", Da = "Dispositivo", Oa = "Sistema", ka = "Mostrar strings solares", Aa = "Mostrar equipo opcional", ja = "Ámbito", Ma = "Este sistema", Na = "Sistema en paralelo", Pa = "Mostrar la energía de hoy", Fa = "Mostrar grupos sin fallos", Ia = "Mostrar módulos de batería", La = "Secciones", Ra = "Tipos de franja", za = "Carga", Ba = "Descarga", Va = "Cargador de VE", Ha = "Mostrar línea de tiempo semanal", Ua = "Flujo de potencia de SAJ Local", Wa = "Potencia en vivo entre solar, batería, red, casa y el equipo opcional", Ga = "Estado de SAJ Local", Ka = "Estado de funcionamiento, modo, lecturas clave, energía de hoy, fallos y si se permite el control", qa = "Fallos de SAJ Local", Ja = "Fallos activos por equipo, con borrar fallo", Ya = "Batería de SAJ Local", Xa = "Estado de carga con reserva y límites, lecturas de la batería y una fila por módulo", Za = "Controles de SAJ Local", Qa = "Los controles compartidos que ofrece el sistema", $a = "Programación de SAJ Local", eo = "Franjas de carga, descarga y del cargador de VE con una línea de tiempo semanal", to = "Días de la semana de SAJ Local", no = {
		choose_system: Ti,
		badge_name: Ei,
		badge_description: Di,
		not_answering: Oi,
		unavailable: ki,
		busy: Ai,
		press: ji,
		week_timeline: Mi,
		locked_message: Ni,
		open_settings: Pi,
		empty_title: Fi,
		empty_enable: Ii,
		open_device_page: Li,
		entity_kind_reading: Ri,
		entity_kind_configuration: zi,
		entity_kind_schedule: Bi,
		solar: Vi,
		battery: Hi,
		grid: "Red",
		home: Ui,
		inverter: Wi,
		ev_charger: Gi,
		backup_load: Ki,
		meter_b: qi,
		charging: Ji,
		discharging: Yi,
		importing: Xi,
		exporting: Zi,
		idle: Qi,
		no_faults: $i,
		faults: ea,
		changes: ta,
		battery_pack: na,
		faults_count_one: ra,
		faults_count_many: ia,
		faults_count_other: aa,
		no_active_faults: oa,
		clear_fault: sa,
		see_diagnostics: ca,
		changes_allowed: la,
		changes_off: ua,
		no_battery: da,
		mode: fa,
		mode_running_now: pa,
		time_of_use_notice: ma,
		slot_number: ha,
		slots_left_out_one: ga,
		slots_left_out_many: _a,
		slots_left_out_other: va,
		weekdays: ya,
		sign_battery: ba,
		sign_grid: xa,
		sign_inverter: Sa,
		section_mode: Ca,
		section_battery: wa,
		section_grid: "Red",
		section_power_control: Ta,
		section_ev_charger: Ea,
		section_device: Da,
		option_device: Oa,
		option_show_strings: ka,
		option_show_optional_equipment: Aa,
		option_scope: ja,
		option_scope_system: Ma,
		option_scope_parallel: Na,
		option_show_energy: Pa,
		option_show_groups_without_faults: Fa,
		option_show_packs: Ia,
		option_sections: La,
		option_slot_kinds: Ra,
		option_kind_charge: za,
		option_kind_discharge: Ba,
		option_kind_ev_charger: Va,
		option_show_timeline: Ha,
		power_flow_card_name: Ua,
		power_flow_card_description: Wa,
		status_card_name: Ga,
		status_card_description: Ka,
		faults_card_name: qa,
		faults_card_description: Ja,
		battery_card_name: Ya,
		battery_card_description: Xa,
		controls_card_name: Za,
		controls_card_description: Qa,
		schedule_card_name: $a,
		schedule_card_description: eo,
		weekdays_feature_name: to
	};
})), io, ao, oo, so, co, lo, uo, fo, po, mo, ho, go, _o, vo, yo, bo, xo, So, Co, wo, To, Eo, Do, Oo, ko, Ao, jo, Mo, No, Po, Fo, Io, Lo, Ro, zo, Bo, Vo, Ho, Uo, Wo, Go, Ko, qo, Jo, Yo, Xo, Zo, Qo, $o, es, ts, ns, rs, is, as, os, ss, cs, ls, us, ds, fs, ps, ms, hs, gs, _s, vs, ys, bs, xs, Ss, Cs, ws, Ts, Es, Ds, Os, ks, As, js, Ms, Ns, Ps, Fs, Is, Ls, Rs, zs = t((() => {
	io = "Choisir un système SAJ Local", ao = "État de SAJ Local", oo = "État de fonctionnement et nombre de défauts actifs d'un système SAJ Local", so = "Ne répond pas", co = "Indisponible", lo = "En cours", uo = "Appuyer", fo = "Chronologie de la semaine", po = "Le contrôle est désactivé pour ce système", mo = "Ouvrir les paramètres", ho = "Rien à afficher pour le moment", go = "Activez les entités de {kind} sur la page de l'appareil du système pour les afficher ici.", _o = "Ouvrir la page de l'appareil", vo = "mesure", yo = "configuration", bo = "programme", xo = "Solaire", So = "Batterie", Co = "Réseau", wo = "Maison", To = "Onduleur", Eo = "Chargeur de VE", Do = "Circuit de secours", Oo = "Compteur B", ko = "Charge", Ao = "Décharge", jo = "Soutirage", Mo = "Injection", No = "Inactif", Po = "Aucun défaut", Fo = "Défauts", Io = "Contrôle", Lo = "Module {number}", Ro = "{count} défaut", zo = "{count} de défauts", Bo = "{count} défauts", Vo = "Aucun défaut actif", Ho = "Effacer le défaut", Uo = "Consultez le téléchargement des diagnostics pour le registre et le bit", Wo = "Contrôle autorisé", Go = "Contrôle désactivé", Ko = "Ce système n'a pas de batterie", qo = "Mode", Jo = "En cours", Yo = "Les plages de charge et de décharge ne s'exécutent qu'en mode horaire", Xo = "Plage {number}", Zo = "{count} plage a des entités désactivées", Qo = "{count} de plages ont des entités désactivées", $o = "{count} plages ont des entités désactivées", es = "Jours de la semaine", ts = "Positif : décharge, négatif : charge", ns = "Positif : injection, négatif : soutirage", rs = "Positif : fournit, négatif : absorbe", is = "Mode", as = "Batterie", os = "Réseau", ss = "Pilotage de puissance", cs = "Chargeur de VE", ls = "Appareil", us = "Système", ds = "Afficher les chaînes solaires", fs = "Afficher l'équipement optionnel", ps = "Périmètre", ms = "Ce système", hs = "Système en parallèle", gs = "Afficher l'énergie du jour", _s = "Afficher les groupes sans défaut", vs = "Afficher les modules de batterie", ys = "Sections", bs = "Types de plages", xs = "Charge", Ss = "Décharge", Cs = "Chargeur de VE", ws = "Afficher la chronologie de la semaine", Ts = "Flux de puissance SAJ Local", Es = "Puissance en direct entre le solaire, la batterie, le réseau, la maison et l'équipement optionnel", Ds = "État de SAJ Local", Os = "État de fonctionnement, mode, mesures clés, énergie du jour, défauts et autorisation du contrôle", ks = "Défauts de SAJ Local", As = "Défauts actifs par équipement, avec effacement du défaut", js = "Batterie de SAJ Local", Ms = "État de charge avec réserve et limites, mesures de la batterie et une ligne par module", Ns = "Contrôle de SAJ Local", Ps = "Les commandes communes que le système propose", Fs = "Programme de SAJ Local", Is = "Plages de charge, de décharge et du chargeur de VE avec une chronologie de la semaine", Ls = "Jours de la semaine de SAJ Local", Rs = {
		choose_system: io,
		badge_name: ao,
		badge_description: oo,
		not_answering: so,
		unavailable: co,
		busy: lo,
		press: uo,
		week_timeline: fo,
		locked_message: po,
		open_settings: mo,
		empty_title: ho,
		empty_enable: go,
		open_device_page: _o,
		entity_kind_reading: vo,
		entity_kind_configuration: yo,
		entity_kind_schedule: bo,
		solar: xo,
		battery: So,
		grid: Co,
		home: wo,
		inverter: To,
		ev_charger: Eo,
		backup_load: Do,
		meter_b: Oo,
		charging: ko,
		discharging: Ao,
		importing: jo,
		exporting: Mo,
		idle: No,
		no_faults: Po,
		faults: Fo,
		changes: Io,
		battery_pack: Lo,
		faults_count_one: Ro,
		faults_count_many: zo,
		faults_count_other: Bo,
		no_active_faults: Vo,
		clear_fault: Ho,
		see_diagnostics: Uo,
		changes_allowed: Wo,
		changes_off: Go,
		no_battery: Ko,
		mode: qo,
		mode_running_now: Jo,
		time_of_use_notice: Yo,
		slot_number: Xo,
		slots_left_out_one: Zo,
		slots_left_out_many: Qo,
		slots_left_out_other: $o,
		weekdays: es,
		sign_battery: ts,
		sign_grid: ns,
		sign_inverter: rs,
		section_mode: is,
		section_battery: as,
		section_grid: os,
		section_power_control: ss,
		section_ev_charger: cs,
		section_device: ls,
		option_device: us,
		option_show_strings: ds,
		option_show_optional_equipment: fs,
		option_scope: ps,
		option_scope_system: ms,
		option_scope_parallel: hs,
		option_show_energy: gs,
		option_show_groups_without_faults: _s,
		option_show_packs: vs,
		option_sections: ys,
		option_slot_kinds: bs,
		option_kind_charge: xs,
		option_kind_discharge: Ss,
		option_kind_ev_charger: Cs,
		option_show_timeline: ws,
		power_flow_card_name: Ts,
		power_flow_card_description: Es,
		status_card_name: Ds,
		status_card_description: Os,
		faults_card_name: ks,
		faults_card_description: As,
		battery_card_name: js,
		battery_card_description: Ms,
		controls_card_name: Ns,
		controls_card_description: Ps,
		schedule_card_name: Fs,
		schedule_card_description: Is,
		weekdays_feature_name: Ls
	};
})), Bs, Vs, Hs, Us, Ws, Gs, Ks, qs, Js, Ys, Xs, Zs, Qs, $s, ec, tc, nc, rc, ic, ac, oc, sc, cc, lc, uc, dc, fc, pc, mc, hc, gc, _c, vc, yc, bc, xc, Sc, Cc, wc, Tc, Ec, Dc, Oc, kc, Ac, jc, Mc, Nc, Pc, Fc, Ic, Lc, Rc, zc, Bc, Vc, Hc, Uc, Wc, Gc, Kc, qc, Jc, Yc, Xc, Zc, Qc, $c, el, tl, nl, rl, il, al, ol, sl, cl, ll, ul, dl, fl, pl, ml, hl, gl, _l, vl, yl, bl = t((() => {
	Bs = "Scegli un sistema SAJ Local", Vs = "Stato di SAJ Local", Hs = "Stato di funzionamento e numero di guasti attivi di un sistema SAJ Local", Us = "Non risponde", Ws = "Non disponibile", Gs = "In corso", Ks = "Premi", qs = "Linea temporale settimanale", Js = "Il controllo è disattivato per questo sistema", Ys = "Apri le impostazioni", Xs = "Ancora nulla da mostrare", Zs = "Abilita le entità di {kind} nella pagina del dispositivo del sistema per mostrarle qui.", Qs = "Apri la pagina del dispositivo", $s = "lettura", ec = "configurazione", tc = "pianificazione", nc = "Solare", rc = "Batteria", ic = "Rete", ac = "Casa", oc = "Inverter", sc = "Caricatore EV", cc = "Carichi di backup", lc = "Contatore B", uc = "In carica", dc = "In scarica", fc = "Prelievo", pc = "Immissione", mc = "Inattivo", hc = "Nessun guasto", gc = "Guasti", _c = "Controllo", vc = "Modulo {number}", yc = "{count} guasto", bc = "{count} guasti", xc = "{count} guasti", Sc = "Nessun guasto attivo", Cc = "Cancella guasto", wc = "Vedi il download diagnostica per il registro e il bit", Tc = "Controllo consentito", Ec = "Controllo disattivato", Dc = "Questo sistema non ha una batteria", Oc = "Modalità", kc = "In esecuzione ora", Ac = "Le fasce di carica e scarica funzionano solo nella modalità a fasce orarie", jc = "Fascia {number}", Mc = "{count} fascia ha entità disabilitate", Nc = "{count} fasce hanno entità disabilitate", Pc = "{count} fasce hanno entità disabilitate", Fc = "Giorni della settimana", Ic = "Positivo scarica, negativo carica", Lc = "Positivo immette, negativo preleva", Rc = "Positivo eroga, negativo assorbe", zc = "Modalità", Bc = "Batteria", Vc = "Rete", Hc = "Controllo della potenza", Uc = "Caricatore EV", Wc = "Dispositivo", Gc = "Sistema", Kc = "Mostra le stringhe solari", qc = "Mostra le apparecchiature opzionali", Jc = "Ambito", Yc = "Questo sistema", Xc = "Sistema in parallelo", Zc = "Mostra l'energia di oggi", Qc = "Mostra i gruppi senza guasti", $c = "Mostra i moduli batteria", el = "Sezioni", tl = "Tipi di fascia", nl = "Carica", rl = "Scarica", il = "Caricatore EV", al = "Mostra la linea temporale settimanale", ol = "Flusso di potenza SAJ Local", sl = "Potenza in tempo reale tra solare, batteria, rete, casa e apparecchiature opzionali", cl = "Stato SAJ Local", ll = "Stato di funzionamento, modalità, letture principali, energia di oggi, guasti e se il controllo è consentito", ul = "Guasti SAJ Local", dl = "Guasti attivi per ogni apparecchiatura, con cancellazione del guasto", fl = "Batteria SAJ Local", pl = "Stato di carica con riserva e limiti, letture della batteria e una riga per ogni modulo", ml = "Controlli SAJ Local", hl = "I controlli condivisi offerti dal sistema", gl = "Pianificazione SAJ Local", _l = "Fasce di carica, scarica e del caricatore EV con una linea temporale settimanale", vl = "Giorni della settimana SAJ Local", yl = {
		choose_system: Bs,
		badge_name: Vs,
		badge_description: Hs,
		not_answering: Us,
		unavailable: Ws,
		busy: Gs,
		press: Ks,
		week_timeline: qs,
		locked_message: Js,
		open_settings: Ys,
		empty_title: Xs,
		empty_enable: Zs,
		open_device_page: Qs,
		entity_kind_reading: $s,
		entity_kind_configuration: ec,
		entity_kind_schedule: tc,
		solar: nc,
		battery: rc,
		grid: ic,
		home: ac,
		inverter: oc,
		ev_charger: sc,
		backup_load: cc,
		meter_b: lc,
		charging: uc,
		discharging: dc,
		importing: fc,
		exporting: pc,
		idle: mc,
		no_faults: hc,
		faults: gc,
		changes: _c,
		battery_pack: vc,
		faults_count_one: yc,
		faults_count_many: bc,
		faults_count_other: xc,
		no_active_faults: Sc,
		clear_fault: Cc,
		see_diagnostics: wc,
		changes_allowed: Tc,
		changes_off: Ec,
		no_battery: Dc,
		mode: Oc,
		mode_running_now: kc,
		time_of_use_notice: Ac,
		slot_number: jc,
		slots_left_out_one: Mc,
		slots_left_out_many: Nc,
		slots_left_out_other: Pc,
		weekdays: Fc,
		sign_battery: Ic,
		sign_grid: Lc,
		sign_inverter: Rc,
		section_mode: zc,
		section_battery: Bc,
		section_grid: Vc,
		section_power_control: Hc,
		section_ev_charger: Uc,
		section_device: Wc,
		option_device: Gc,
		option_show_strings: Kc,
		option_show_optional_equipment: qc,
		option_scope: Jc,
		option_scope_system: Yc,
		option_scope_parallel: Xc,
		option_show_energy: Zc,
		option_show_groups_without_faults: Qc,
		option_show_packs: $c,
		option_sections: el,
		option_slot_kinds: tl,
		option_kind_charge: nl,
		option_kind_discharge: rl,
		option_kind_ev_charger: il,
		option_show_timeline: al,
		power_flow_card_name: ol,
		power_flow_card_description: sl,
		status_card_name: cl,
		status_card_description: ll,
		faults_card_name: ul,
		faults_card_description: dl,
		battery_card_name: fl,
		battery_card_description: pl,
		controls_card_name: ml,
		controls_card_description: hl,
		schedule_card_name: gl,
		schedule_card_description: _l,
		weekdays_feature_name: vl
	};
})), xl, Sl, Cl, wl, Tl, El, Dl, Ol, kl, Al, jl, Ml, Nl, Pl, Fl, Il, Ll, Rl, zl, Bl, Vl, Hl, Ul, Wl, Gl, Kl, ql, Jl, Yl, Xl, Zl, Ql, $l, eu, tu, nu, ru, iu, au, ou, su, cu, lu, uu, du, fu, pu, mu, hu, gu, _u, vu, yu, bu, xu, Su, Cu, wu, Tu, Eu, Du, Ou, ku, Au, ju, Mu, Nu, Pu, Fu, Iu, Lu, Ru, zu, Bu, Vu, Hu, Uu, Wu, Gu, Ku, qu, Ju, Yu, Xu = t((() => {
	xl = "Kies een SAJ Local-systeem", Sl = "SAJ Local-status", Cl = "Bedrijfstoestand en aantal actieve storingen van een SAJ Local-systeem", wl = "Antwoordt niet", Tl = "Niet beschikbaar", El = "Bezig", Dl = "Indrukken", Ol = "Weektijdlijn", kl = "Bediening is uitgeschakeld voor dit systeem", Al = "Instellingen openen", jl = "Nog niets om te tonen", Ml = "Schakel {kind}-entiteiten in op de apparaatpagina van het systeem om ze hier te tonen.", Nl = "Apparaatpagina openen", Pl = "meting", Fl = "configuratie", Il = "schema", Ll = "Batterij", Rl = "Huis", zl = "Omvormer", Bl = "EV-lader", Vl = "Back-upbelasting", Hl = "Meter B", Ul = "Opladen", Wl = "Ontladen", Gl = "Afname", Kl = "Teruglevering", ql = "Inactief", Jl = "Geen storingen", Yl = "Storingen", Xl = "Bediening", Zl = "Pack {number}", Ql = "{count} storing", $l = "{count} storingen", eu = "Geen actieve storingen", tu = "Storing wissen", nu = "Zie de diagnosedownload voor het register en de bit", ru = "Bediening toegestaan", iu = "Bediening uit", au = "Dit systeem heeft geen batterij", ou = "Modus", su = "Nu actief", cu = "Oplaad- en ontlaadtijdvakken worden alleen uitgevoerd in de tijdgestuurde modus", lu = "Tijdvak {number}", uu = "{count} tijdvak heeft uitgeschakelde entiteiten", du = "{count} tijdvakken hebben uitgeschakelde entiteiten", fu = "Dagen van de week", pu = "Positief ontlaadt, negatief laadt op", mu = "Positief levert terug, negatief neemt af", hu = "Positief levert af, negatief neemt op", gu = "Modus", _u = "Batterij", vu = "Vermogensregeling", yu = "EV-lader", bu = "Apparaat", xu = "Systeem", Su = "Zonnestrings tonen", Cu = "Optionele apparatuur tonen", wu = "Bereik", Tu = "Dit systeem", Eu = "Parallel systeem", Du = "Energie van vandaag tonen", Ou = "Groepen zonder storingen tonen", ku = "Batterijpacks tonen", Au = "Secties", ju = "Soorten tijdvakken", Mu = "Opladen", Nu = "Ontladen", Pu = "EV-lader", Fu = "Weektijdlijn tonen", Iu = "SAJ Local-vermogensstroom", Lu = "Live vermogen tussen zon, batterij, net, huis en de optionele apparatuur", Ru = "SAJ Local-status", zu = "Bedrijfstoestand, modus, belangrijke metingen, energie van vandaag, storingen en of bediening is toegestaan", Bu = "SAJ Local-storingen", Vu = "Actieve storingen per onderdeel van de apparatuur, met storing wissen", Hu = "SAJ Local-batterij", Uu = "Laadniveau met reserve en limieten, batterijmetingen en één rij per pack", Wu = "SAJ Local-bediening", Gu = "De gedeelde bediening die het systeem biedt", Ku = "SAJ Local-schema", qu = "Oplaad-, ontlaad- en EV-ladertijdvakken met een weektijdlijn", Ju = "SAJ Local-weekdagen", Yu = {
		choose_system: xl,
		badge_name: Sl,
		badge_description: Cl,
		not_answering: wl,
		unavailable: Tl,
		busy: El,
		press: Dl,
		week_timeline: Ol,
		locked_message: kl,
		open_settings: Al,
		empty_title: jl,
		empty_enable: Ml,
		open_device_page: Nl,
		entity_kind_reading: Pl,
		entity_kind_configuration: Fl,
		entity_kind_schedule: Il,
		solar: "Zon",
		battery: Ll,
		grid: "Net",
		home: Rl,
		inverter: zl,
		ev_charger: Bl,
		backup_load: Vl,
		meter_b: Hl,
		charging: Ul,
		discharging: Wl,
		importing: Gl,
		exporting: Kl,
		idle: ql,
		no_faults: Jl,
		faults: Yl,
		changes: Xl,
		battery_pack: Zl,
		faults_count_one: Ql,
		faults_count_other: $l,
		no_active_faults: eu,
		clear_fault: tu,
		see_diagnostics: nu,
		changes_allowed: ru,
		changes_off: iu,
		no_battery: au,
		mode: ou,
		mode_running_now: su,
		time_of_use_notice: cu,
		slot_number: lu,
		slots_left_out_one: uu,
		slots_left_out_other: du,
		weekdays: fu,
		sign_battery: pu,
		sign_grid: mu,
		sign_inverter: hu,
		section_mode: gu,
		section_battery: _u,
		section_grid: "Net",
		section_power_control: vu,
		section_ev_charger: yu,
		section_device: bu,
		option_device: xu,
		option_show_strings: Su,
		option_show_optional_equipment: Cu,
		option_scope: wu,
		option_scope_system: Tu,
		option_scope_parallel: Eu,
		option_show_energy: Du,
		option_show_groups_without_faults: Ou,
		option_show_packs: ku,
		option_sections: Au,
		option_slot_kinds: ju,
		option_kind_charge: Mu,
		option_kind_discharge: Nu,
		option_kind_ev_charger: Pu,
		option_show_timeline: Fu,
		power_flow_card_name: Iu,
		power_flow_card_description: Lu,
		status_card_name: Ru,
		status_card_description: zu,
		faults_card_name: Bu,
		faults_card_description: Vu,
		battery_card_name: Hu,
		battery_card_description: Uu,
		controls_card_name: Wu,
		controls_card_description: Gu,
		schedule_card_name: Ku,
		schedule_card_description: qu,
		weekdays_feature_name: Ju
	};
})), Zu, Qu, $u, ed, td, nd, rd, id, ad, od, sd, cd, ld, ud, dd, fd, pd, md, hd, gd, _d, vd, yd, bd, xd, Sd, Cd, wd, Td, Ed, Dd, Od, kd, Ad, jd, Md, Nd, Pd, Fd, Id, Ld, Rd, zd, Bd, Vd, Hd, Ud, Wd, Gd, Kd, qd, Jd, Yd, Xd, Zd, Qd, $d, ef, tf, nf, rf, af, of, sf, cf, lf, uf, df, ff, pf, mf, hf, gf, _f, vf, yf, bf, xf, Sf, Cf, wf, Tf, Ef, Df, Of, kf, Af, jf, Mf, Nf = t((() => {
	Zu = "Wybierz system SAJ Local", Qu = "Stan SAJ Local", $u = "Stan pracy i liczba aktywnych usterek systemu SAJ Local", ed = "Nie odpowiada", td = "Niedostępny", nd = "Pracuje", rd = "Naciśnij", id = "Oś czasu tygodnia", ad = "Sterowanie jest wyłączone dla tego systemu", od = "Otwórz ustawienia", sd = "Nie ma jeszcze nic do pokazania", cd = "Włącz encje typu {kind} na stronie urządzenia systemu, aby pokazać je tutaj.", ld = "Otwórz stronę urządzenia", ud = "odczyt", dd = "konfiguracja", fd = "harmonogram", pd = "Słońce", md = "Bateria", hd = "Sieć", gd = "Falownik", _d = "Ładowarka EV", vd = "Odbiory awaryjne", yd = "Licznik B", bd = "Ładowanie", xd = "Rozładowanie", Sd = "Pobór", Cd = "Oddawanie", wd = "Bezczynny", Td = "Brak usterek", Ed = "Usterki", Dd = "Sterowanie", Od = "Moduł {number}", kd = "{count} usterka", Ad = "{count} usterki", jd = "{count} usterek", Md = "{count} usterki", Nd = "Brak aktywnych usterek", Pd = "Wyczyść usterkę", Fd = "Rejestr i bit znajdziesz w pobranej diagnostyce", Id = "Sterowanie dozwolone", Ld = "Sterowanie wyłączone", Rd = "Ten system nie ma baterii", zd = "Tryb", Bd = "Działa teraz", Vd = "Przedziały ładowania i rozładowania działają tylko w trybie taryfy czasowej", Hd = "Przedział {number}", Ud = "{count} przedział ma wyłączone encje", Wd = "{count} przedziały mają wyłączone encje", Gd = "{count} przedziałów ma wyłączone encje", Kd = "{count} przedziału ma wyłączone encje", qd = "Dni tygodnia", Jd = "Wartość dodatnia rozładowuje, ujemna ładuje", Yd = "Wartość dodatnia oddaje, ujemna pobiera", Xd = "Wartość dodatnia oddaje moc, ujemna ją pobiera", Zd = "Tryb", Qd = "Bateria", $d = "Sieć", ef = "Sterowanie mocą", tf = "Ładowarka EV", nf = "Urządzenie", rf = "System", af = "Pokaż ciągi paneli", of = "Pokaż wyposażenie opcjonalne", sf = "Zakres", cf = "Ten system", lf = "System równoległy", uf = "Pokaż dzisiejszą energię", df = "Pokaż grupy bez usterek", ff = "Pokaż moduły baterii", pf = "Sekcje", mf = "Rodzaje przedziałów", hf = "Ładowanie", gf = "Rozładowanie", _f = "Ładowarka EV", vf = "Pokaż oś czasu tygodnia", yf = "Przepływ mocy SAJ Local", bf = "Bieżący przepływ mocy między słońcem, baterią, siecią, domem i wyposażeniem opcjonalnym", xf = "Stan SAJ Local", Sf = "Stan pracy, tryb, kluczowe odczyty, dzisiejsza energia, usterki i informacja, czy sterowanie jest dozwolone", Cf = "Usterki SAJ Local", wf = "Aktywne usterki według elementu wyposażenia, z przyciskiem Wyczyść usterkę", Tf = "Bateria SAJ Local", Ef = "Stan naładowania z rezerwą i limitami, odczyty baterii i jeden wiersz dla każdego modułu", Df = "Sterowanie SAJ Local", Of = "Wspólne elementy sterowania, które oferuje system", kf = "Harmonogram SAJ Local", Af = "Przedziały ładowania, rozładowania i ładowarki EV z osią czasu tygodnia", jf = "Dni tygodnia SAJ Local", Mf = {
		choose_system: Zu,
		badge_name: Qu,
		badge_description: $u,
		not_answering: ed,
		unavailable: td,
		busy: nd,
		press: rd,
		week_timeline: id,
		locked_message: ad,
		open_settings: od,
		empty_title: sd,
		empty_enable: cd,
		open_device_page: ld,
		entity_kind_reading: ud,
		entity_kind_configuration: dd,
		entity_kind_schedule: fd,
		solar: pd,
		battery: md,
		grid: hd,
		home: "Dom",
		inverter: gd,
		ev_charger: _d,
		backup_load: vd,
		meter_b: yd,
		charging: bd,
		discharging: xd,
		importing: Sd,
		exporting: Cd,
		idle: wd,
		no_faults: Td,
		faults: Ed,
		changes: Dd,
		battery_pack: Od,
		faults_count_one: kd,
		faults_count_few: Ad,
		faults_count_many: jd,
		faults_count_other: Md,
		no_active_faults: Nd,
		clear_fault: Pd,
		see_diagnostics: Fd,
		changes_allowed: Id,
		changes_off: Ld,
		no_battery: Rd,
		mode: zd,
		mode_running_now: Bd,
		time_of_use_notice: Vd,
		slot_number: Hd,
		slots_left_out_one: Ud,
		slots_left_out_few: Wd,
		slots_left_out_many: Gd,
		slots_left_out_other: Kd,
		weekdays: qd,
		sign_battery: Jd,
		sign_grid: Yd,
		sign_inverter: Xd,
		section_mode: Zd,
		section_battery: Qd,
		section_grid: $d,
		section_power_control: ef,
		section_ev_charger: tf,
		section_device: nf,
		option_device: rf,
		option_show_strings: af,
		option_show_optional_equipment: of,
		option_scope: sf,
		option_scope_system: cf,
		option_scope_parallel: lf,
		option_show_energy: uf,
		option_show_groups_without_faults: df,
		option_show_packs: ff,
		option_sections: pf,
		option_slot_kinds: mf,
		option_kind_charge: hf,
		option_kind_discharge: gf,
		option_kind_ev_charger: _f,
		option_show_timeline: vf,
		power_flow_card_name: yf,
		power_flow_card_description: bf,
		status_card_name: xf,
		status_card_description: Sf,
		faults_card_name: Cf,
		faults_card_description: wf,
		battery_card_name: Tf,
		battery_card_description: Ef,
		controls_card_name: Df,
		controls_card_description: Of,
		schedule_card_name: kf,
		schedule_card_description: Af,
		weekdays_feature_name: jf
	};
})), Pf, Ff, If, Lf, Rf, zf, Bf, Vf, Hf, Uf, Wf, Gf, Kf, qf, Jf, Yf, Xf, Zf, Qf, $f, ep, tp, np, rp, ip, ap, op, sp, cp, lp, up, dp, fp, pp, mp, hp, gp, _p, vp, yp, bp, xp, Sp, Cp, wp, Tp, Ep, Dp, Op, kp, Ap, jp, Mp, Np, Pp, Fp, Ip, Lp, Rp, zp, Bp, Vp, Hp, Up, Wp, Gp, Kp, qp, Jp, Yp, Xp, Zp, Qp, $p, em, tm, nm, rm, im, am, om, sm, cm, lm = t((() => {
	Pf = "Välj ett SAJ Local-system", Ff = "SAJ Local-status", If = "Driftläge och antal aktiva fel för ett SAJ Local-system", Lf = "Svarar inte", Rf = "Otillgänglig", zf = "Arbetar", Bf = "Tryck", Vf = "Veckotidslinje", Hf = "Styrning är av för det här systemet", Uf = "Öppna inställningar", Wf = "Inget att visa ännu", Gf = "Aktivera entiteterna för {kind} på systemets enhetssida för att visa dem här.", Kf = "Öppna enhetssidan", qf = "avläsning", Jf = "konfiguration", Yf = "schema", Xf = "Batteri", Zf = "Nät", Qf = "Växelriktare", $f = "Elbilsladdare", ep = "Reservlast", tp = "Mätare B", np = "Laddar", rp = "Laddar ur", ip = "Import", ap = "Export", op = "Overksam", sp = "Inga fel", cp = "Styrning", lp = "Pack {number}", up = "{count} fel", dp = "{count} fel", fp = "Inga aktiva fel", pp = "Rensa fel", mp = "Se diagnostiknedladdningen för register och bit", hp = "Styrning tillåten", gp = "Styrning av", _p = "Det här systemet har inget batteri", vp = "Läge", yp = "Körs nu", bp = "Tidsluckor för laddning och urladdning körs bara i läget tidsstyrning", xp = "Tidslucka {number}", Sp = "{count} tidslucka har inaktiverade entiteter", Cp = "{count} tidsluckor har inaktiverade entiteter", wp = "Veckodagar", Tp = "Positivt laddar ur, negativt laddar", Ep = "Positivt exporterar, negativt importerar", Dp = "Positivt avger, negativt tar in", Op = "Läge", kp = "Batteri", Ap = "Nät", jp = "Effektstyrning", Mp = "Elbilsladdare", Np = "Enhet", Pp = "System", Fp = "Visa solcellssträngar", Ip = "Visa valfri utrustning", Lp = "Omfång", Rp = "Det här systemet", zp = "Parallellsystem", Bp = "Visa dagens energi", Vp = "Visa grupper utan fel", Hp = "Visa batteripack", Up = "Sektioner", Wp = "Typer av tidsluckor", Gp = "Laddning", Kp = "Urladdning", qp = "Elbilsladdare", Jp = "Visa veckotidslinje", Yp = "SAJ Local effektflöde", Xp = "Live-effekt mellan sol, batteri, nät, hem och den valfria utrustningen", Zp = "SAJ Local-status", Qp = "Driftläge, läge, viktiga avläsningar, dagens energi, fel och om styrning är tillåten", $p = "SAJ Local-fel", em = "Aktiva fel per utrustning, med rensa fel", tm = "SAJ Local-batteri", nm = "Laddningsnivå med reserv och gränser, batteriavläsningar och en rad per pack", rm = "SAJ Local-styrning", im = "De gemensamma styrningarna som systemet erbjuder", am = "SAJ Local-schema", om = "Tidsluckor för laddning, urladdning och elbilsladdare med en veckotidslinje", sm = "SAJ Local-veckodagar", cm = {
		choose_system: Pf,
		badge_name: Ff,
		badge_description: If,
		not_answering: Lf,
		unavailable: Rf,
		busy: zf,
		press: Bf,
		week_timeline: Vf,
		locked_message: Hf,
		open_settings: Uf,
		empty_title: Wf,
		empty_enable: Gf,
		open_device_page: Kf,
		entity_kind_reading: qf,
		entity_kind_configuration: Jf,
		entity_kind_schedule: Yf,
		solar: "Sol",
		battery: Xf,
		grid: Zf,
		home: "Hem",
		inverter: Qf,
		ev_charger: $f,
		backup_load: ep,
		meter_b: tp,
		charging: np,
		discharging: rp,
		importing: ip,
		exporting: ap,
		idle: op,
		no_faults: sp,
		faults: "Fel",
		changes: cp,
		battery_pack: lp,
		faults_count_one: up,
		faults_count_other: dp,
		no_active_faults: fp,
		clear_fault: pp,
		see_diagnostics: mp,
		changes_allowed: hp,
		changes_off: gp,
		no_battery: _p,
		mode: vp,
		mode_running_now: yp,
		time_of_use_notice: bp,
		slot_number: xp,
		slots_left_out_one: Sp,
		slots_left_out_other: Cp,
		weekdays: wp,
		sign_battery: Tp,
		sign_grid: Ep,
		sign_inverter: Dp,
		section_mode: Op,
		section_battery: kp,
		section_grid: Ap,
		section_power_control: jp,
		section_ev_charger: Mp,
		section_device: Np,
		option_device: Pp,
		option_show_strings: Fp,
		option_show_optional_equipment: Ip,
		option_scope: Lp,
		option_scope_system: Rp,
		option_scope_parallel: zp,
		option_show_energy: Bp,
		option_show_groups_without_faults: Vp,
		option_show_packs: Hp,
		option_sections: Up,
		option_slot_kinds: Wp,
		option_kind_charge: Gp,
		option_kind_discharge: Kp,
		option_kind_ev_charger: qp,
		option_show_timeline: Jp,
		power_flow_card_name: Yp,
		power_flow_card_description: Xp,
		status_card_name: Zp,
		status_card_description: Qp,
		faults_card_name: $p,
		faults_card_description: em,
		battery_card_name: tm,
		battery_card_description: nm,
		controls_card_name: rm,
		controls_card_description: im,
		schedule_card_name: am,
		schedule_card_description: om,
		weekdays_feature_name: sm
	};
})), um, dm, fm, pm, mm, hm, gm, _m, vm, ym, bm, xm, Sm, Cm, wm, Tm, Em, Dm, Om, km, Am, jm, Mm, Nm, Pm, Fm, Im, Lm, Rm, zm, Bm, Vm, Hm, Um, Wm, Gm, Km, qm, Jm, Ym, Xm, Zm, Qm, $m, eh, th, nh, rh, ih, ah, oh, sh, ch, lh, uh, dh, fh, ph, mh, hh, gh, _h, vh, yh, bh, xh, Sh, Ch, wh, Th, Eh, Dh, Oh, kh, Ah, jh, Mh, Nh, Ph, Fh, Ih, Lh, Rh, zh, Bh = t((() => {
	um = "选择一个 SAJ Local 系统", dm = "SAJ Local 状态", fm = "SAJ Local 系统的运行状态和当前故障数量", pm = "无响应", mm = "不可用", hm = "处理中", gm = "按下", _m = "一周时间线", vm = "此系统的控制已关闭", ym = "打开设置", bm = "暂无内容可显示", xm = "在系统的设备页面启用{kind}实体，即可在此显示。", Sm = "打开设备页面", Cm = "读数", wm = "配置", Tm = "计划", Em = "光伏", Dm = "电池", Om = "电网", km = "家庭", Am = "逆变器", jm = "充电桩", Mm = "备用负载", Nm = "电表 B", Pm = "充电", Fm = "放电", Im = "购电", Lm = "馈电", Rm = "空闲", zm = "无故障", Bm = "故障", Vm = "控制", Hm = "电池包 {number}", Um = "{count} 个故障", Wm = "无当前故障", Gm = "清除故障", Km = "寄存器和位请查看诊断下载", qm = "允许控制", Jm = "控制已关闭", Ym = "此系统没有电池", Xm = "模式", Zm = "当前运行", Qm = "充电和放电时段只在分时模式下运行", $m = "时段 {number}", eh = "{count} 个时段有已禁用的实体", th = "星期", nh = "正值为放电，负值为充电", rh = "正值为馈电，负值为购电", ih = "正值为输出，负值为输入", ah = "模式", oh = "电池", sh = "电网", ch = "功率控制", lh = "充电桩", uh = "设备", dh = "系统", fh = "显示光伏组串", ph = "显示可选设备", mh = "范围", hh = "此系统", gh = "并机系统", _h = "显示今日电量", vh = "显示无故障的分组", yh = "显示电池包", bh = "分区", xh = "时段类型", Sh = "充电", Ch = "放电", wh = "充电桩", Th = "显示一周时间线", Eh = "SAJ Local 功率流", Dh = "光伏、电池、电网、家庭和可选设备之间的实时功率", Oh = "SAJ Local 状态", kh = "运行状态、模式、关键读数、今日电量、故障，以及是否允许控制", Ah = "SAJ Local 故障", jh = "按设备列出当前故障，并可清除故障", Mh = "SAJ Local 电池", Nh = "荷电状态、备用电量和限制、电池读数，以及每个电池包一行", Ph = "SAJ Local 控制", Fh = "系统提供的共用控制项", Ih = "SAJ Local 计划", Lh = "充电、放电和充电桩时段，附一周时间线", Rh = "SAJ Local 星期", zh = {
		choose_system: um,
		badge_name: dm,
		badge_description: fm,
		not_answering: pm,
		unavailable: mm,
		busy: hm,
		press: gm,
		week_timeline: _m,
		locked_message: vm,
		open_settings: ym,
		empty_title: bm,
		empty_enable: xm,
		open_device_page: Sm,
		entity_kind_reading: Cm,
		entity_kind_configuration: wm,
		entity_kind_schedule: Tm,
		solar: Em,
		battery: Dm,
		grid: Om,
		home: km,
		inverter: Am,
		ev_charger: jm,
		backup_load: Mm,
		meter_b: Nm,
		charging: Pm,
		discharging: Fm,
		importing: Im,
		exporting: Lm,
		idle: Rm,
		no_faults: zm,
		faults: Bm,
		changes: Vm,
		battery_pack: Hm,
		faults_count_other: Um,
		no_active_faults: Wm,
		clear_fault: Gm,
		see_diagnostics: Km,
		changes_allowed: qm,
		changes_off: Jm,
		no_battery: Ym,
		mode: Xm,
		mode_running_now: Zm,
		time_of_use_notice: Qm,
		slot_number: $m,
		slots_left_out_other: eh,
		weekdays: th,
		sign_battery: nh,
		sign_grid: rh,
		sign_inverter: ih,
		section_mode: ah,
		section_battery: oh,
		section_grid: sh,
		section_power_control: ch,
		section_ev_charger: lh,
		section_device: uh,
		option_device: dh,
		option_show_strings: fh,
		option_show_optional_equipment: ph,
		option_scope: mh,
		option_scope_system: hh,
		option_scope_parallel: gh,
		option_show_energy: _h,
		option_show_groups_without_faults: vh,
		option_show_packs: yh,
		option_sections: bh,
		option_slot_kinds: xh,
		option_kind_charge: Sh,
		option_kind_discharge: Ch,
		option_kind_ev_charger: wh,
		option_show_timeline: Th,
		power_flow_card_name: Eh,
		power_flow_card_description: Dh,
		status_card_name: Oh,
		status_card_description: kh,
		faults_card_name: Ah,
		faults_card_description: jh,
		battery_card_name: Mh,
		battery_card_description: Nh,
		controls_card_name: Ph,
		controls_card_description: Fh,
		schedule_card_name: Ih,
		schedule_card_description: Lh,
		weekdays_feature_name: Rh
	};
})), Vh, Hh, Uh, Wh, Gh, Kh, qh, Jh, O, Yh, Xh, Zh = t((() => {
	Gn(), wi(), ro(), zs(), bl(), Xu(), Nf(), lm(), Bh(), Vh = /* #__PURE__ */ Object.assign({
		"./de.json": Wn,
		"./en.json": Ci,
		"./es.json": no,
		"./fr.json": Rs,
		"./it.json": yl,
		"./nl.json": Yu,
		"./pl.json": Mf,
		"./sv.json": cm,
		"./zh-Hans.json": zh
	}), Hh = /^\.\/|\.json$/g, Uh = () => new Map(Object.entries(Vh).map(([e, t]) => [e.replace(Hh, "").toLowerCase(), t])), Wh = ({ language: e, available: t }) => {
		let n = e.toLowerCase().replaceAll("_", "-");
		return [n, n.replace(/-.*$/, "")].find((e) => t.has(e)) ?? "en";
	}, Gh = ({ template: e, values: t }) => e.replace(/\{(\w+)\}/g, (e, n) => n in t ? String(t[n]) : e), Kh = ({ language: e, available: t }) => {
		let n = t.get(Wh({
			language: e,
			available: t
		})), r = t.get("en"), i = new Intl.PluralRules(e), a = (e) => n?.[e] ?? r?.[e];
		return (e, t = {}) => {
			let n = t.count, r = typeof n == "number" ? `${e}_${i.select(n)}` : void 0, o = (r === void 0 ? void 0 : a(r)) ?? a(e) ?? e;
			return Gh({
				template: o,
				values: t
			});
		};
	}, qh = /* @__PURE__ */ new Map(), Jh = (e) => {
		let t = qh.get(e);
		if (t !== void 0) return t;
		let n = Kh({
			language: e,
			available: Uh()
		});
		return qh.set(e, n), n;
	}, O = () => Jh(document.documentElement.lang || "en"), Yh = [
		{
			name: "day",
			seconds: 86400
		},
		{
			name: "hour",
			seconds: 3600
		},
		{
			name: "minute",
			seconds: 60
		}
	], Xh = ({ from: e, now: t, language: n }) => {
		let r = Math.round((e.getTime() - t.getTime()) / 1e3), i = new Intl.RelativeTimeFormat(n, { numeric: "auto" }), a = Yh.find((e) => Math.abs(r) >= e.seconds);
		return a === void 0 ? i.format(r, "second") : i.format(Math.round(r / a.seconds), a.name);
	};
})), Qh, $h, eg, tg, ng, rg, k, ig, A, ag, j, M, N = t((() => {
	Qh = "saj_local", $h = "unavailable", eg = "unknown", tg = (e) => e.platform === "saj_local" && e.device_id !== null && typeof e.translation_key == "string" && e.translation_key !== "", ng = (e) => {
		let t = new Set(Object.values(e.entities).filter(tg).map((e) => e.device_id));
		return Object.values(e.devices).filter((e) => t.has(e.id));
	}, rg = ({ hass: e, deviceId: t }) => Object.values(e.entities).filter((e) => tg(e) && e.device_id === t).map((e) => e.entity_id), k = ({ hass: e, deviceId: t }) => {
		let n = /* @__PURE__ */ new Map();
		for (let r of Object.values(e.entities)) {
			let i = e.states[r.entity_id];
			tg(r) && r.device_id === t && i !== void 0 && n.set(r.translation_key, {
				key: r.translation_key,
				entityId: r.entity_id,
				domain: r.entity_id.replace(/\..*$/, ""),
				state: i
			});
		}
		return n;
	}, ig = ({ hass: e, entityId: t }) => {
		let n = e.entities[t];
		return n === void 0 || !tg(n) ? null : {
			deviceId: n.device_id,
			key: n.translation_key
		};
	}, A = (e) => e.state.state === $h, ag = (e) => e.length > 0 && e.every(A), j = (e) => {
		let { state: t } = e.state;
		if (t === $h || t === eg || t === "") return null;
		let n = Number(t);
		return Number.isFinite(n) ? n : null;
	}, M = (e) => e?.state.state === "on";
})), P, og, sg, F, I, L = t((() => {
	Zh(), N(), P = ({ name: e, fallback: t }) => ({
		name: e,
		default: t,
		selector: { boolean: {} }
	}), og = ({ name: e, options: t, fallback: n }) => ({
		name: e,
		default: n,
		selector: { select: {
			options: t,
			mode: "dropdown"
		} }
	}), sg = {
		name: "device",
		required: !0,
		selector: { device: { filter: { integration: Qh } } }
	}, F = (e) => {
		let t = O();
		return {
			schema: [sg, ...e(t)],
			computeLabel: (e) => t(`option_${e.name}`)
		};
	}, I = (e) => {
		let [t] = ng(e);
		return t === void 0 ? {} : { device: t.id };
	};
})), R, cg, lg, z = t((() => {
	Zh(), R = ({ type: e, nameKey: t, descriptionKey: n, preview: r }) => {
		window.customCards ??= [], window.customCards.push({
			type: e,
			preview: r,
			get name() {
				return O()(t);
			},
			get description() {
				return O()(n);
			}
		});
	}, cg = ({ type: e, nameKey: t, isSupported: n, configurable: r }) => {
		window.customCardFeatures ??= [], window.customCardFeatures.push({
			type: e,
			isSupported: n,
			configurable: r,
			get name() {
				return O()(t);
			}
		});
	}, lg = ({ type: e, nameKey: t, descriptionKey: n }) => {
		window.customBadges ??= [], window.customBadges.push({
			type: e,
			get name() {
				return O()(t);
			},
			get description() {
				return O()(n);
			}
		});
	};
})), B, ug, dg, fg, pg, mg, hg = t((() => {
	N(), B = [
		{
			id: "inverter",
			summaryKey: "inverter_fault",
			prefix: "inverter"
		},
		{
			id: "battery",
			summaryKey: "battery_fault",
			prefix: "battery"
		},
		{
			id: "ev",
			summaryKey: "ev_fault",
			prefix: "ev"
		}
	], ug = /^battery_pack\d+_(fault|warning)$/, dg = "_fault_unrecognised", fg = ({ definition: e, key: t }) => t.startsWith(`${e.prefix}_fault_`) || e.id === "battery" && ug.test(t), pg = (e) => B.flatMap((t) => {
		let n = e.get(t.summaryKey);
		if (n === void 0) return [];
		let r = [...e.values()].filter((e) => e.domain === "binary_sensor" && M(e) && fg({
			definition: t,
			key: e.key
		})).sort((e, t) => e.key.localeCompare(t.key)).map((e) => ({
			entity: e,
			since: new Date(e.state.last_changed),
			unrecognised: e.key.endsWith(dg)
		}));
		return [{
			id: t.id,
			summary: n,
			active: M(n),
			rows: r
		}];
	}), mg = (e) => B.flatMap((t) => {
		let n = e.get(t.summaryKey);
		return n !== void 0 && M(n) ? [n] : [];
	});
})), gg, _g, vg = t((() => {
	gg = new Map(Object.entries({
		operating: "primary",
		off_grid: "warning",
		grid_connected_load_bypass: "warning",
		fault: "error",
		initialisation: "secondary",
		standby: "secondary",
		upgrade: "secondary",
		debugging: "secondary",
		self_check: "secondary",
		reset: "secondary"
	})), _g = (e) => gg.get(e ?? "") ?? "disabled";
})), yg, bg, xg, Sg, Cg, wg, Tg, Eg, Dg, Og, kg, Ag, jg, Mg, Ng, Pg, Fg, Ig, Lg = t((() => {
	yg = "M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", bg = "M16.67,4H15V2H9V4H7.33A1.33,1.33 0 0,0 6,5.33V20.67C6,21.4 6.6,22 7.33,22H16.67A1.33,1.33 0 0,0 18,20.67V5.33C18,4.6 17.4,4 16.67,4Z", xg = "M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z", Sg = "M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z", Cg = "M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z", wg = "M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z", Tg = "M12.43 11C12.28 10.84 10 7 7 7S2.32 10.18 2 11V13H11.57C11.72 13.16 14 17 17 17S21.68 13.82 22 13V11H12.43M7 9C8.17 9 9.18 9.85 10 11H4.31C4.78 10.17 5.54 9 7 9M17 15C15.83 15 14.82 14.15 14 13H19.69C19.22 13.83 18.46 15 17 15Z", Eg = "M19.77,7.23L19.78,7.22L16.06,3.5L15,4.56L17.11,6.67C16.17,7.03 15.5,7.93 15.5,9A2.5,2.5 0 0,0 18,11.5C18.36,11.5 18.69,11.42 19,11.29V18.5A1,1 0 0,1 18,19.5A1,1 0 0,1 17,18.5V14A2,2 0 0,0 15,12H14V5A2,2 0 0,0 12,3H6A2,2 0 0,0 4,5V21H14V13.5H15.5V18.5A2.5,2.5 0 0,0 18,21A2.5,2.5 0 0,0 20.5,18.5V9C20.5,8.31 20.22,7.68 19.77,7.23M18,10A1,1 0 0,1 17,9A1,1 0 0,1 18,8A1,1 0 0,1 19,9A1,1 0 0,1 18,10M8,18V13.5H6L10,6V11H12L8,18Z", Dg = "M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z", Og = "M12 20L5 20V12H2L12 3L14.78 5.5H14V7.17C12.84 7.58 12 8.7 12 10V20M15 9H16V7.5H20V9H21C21.55 9 22 9.45 22 10V21C22 21.55 21.55 22 21 22H15C14.45 22 14 21.55 14 21V10C14 9.45 14.45 9 15 9M16 11V14H20V11H16Z", kg = "M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", Ag = "M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z", jg = "M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z", Mg = "M12 2C7.04 2 3 6.04 3 11C3 14.91 5.5 18.24 9 19.47V22H11V19.94C11.33 20 11.66 20 12 20S12.67 20 13 19.94V22H15V19.47C18.5 18.23 21 14.9 21 11C21 6.04 16.96 2 12 2M14.25 14L11.25 17L9.75 15.5L11 14.25L9.75 13L12.75 10L14.25 11.5L13 12.75L14.25 14M16 9H8V7H16V9Z", Ng = "M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13", Pg = "M11.45,2V5.55L15,3.77L11.45,2M10.45,8L8,10.46L11.75,11.71L10.45,8M2,11.45L3.77,15L5.55,11.45H2M10,2H2V10C2.57,10.17 3.17,10.25 3.77,10.25C7.35,10.26 10.26,7.35 10.27,3.75C10.26,3.16 10.17,2.57 10,2M17,22V16H14L19,7V13H22L17,22Z", Fg = "M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z", Ig = "M8.28,5.45L6.5,4.55L7.76,2H16.23L17.5,4.55L15.72,5.44L15,4H9L8.28,5.45M18.62,8H14.09L13.3,5H10.7L9.91,8H5.38L4.1,10.55L5.89,11.44L6.62,10H17.38L18.1,11.45L19.89,10.56L18.62,8M17.77,22H15.7L15.46,21.1L12,15.9L8.53,21.1L8.3,22H6.23L9.12,11H11.19L10.83,12.35L12,14.1L13.16,12.35L12.81,11H14.88L17.77,22M11.4,15L10.5,13.65L9.32,18.13L11.4,15M14.68,18.12L13.5,13.64L12.6,15L14.68,18.12Z";
})), Rg, zg = t((() => {
	Lg(), Rg = {
		solar: Pg,
		battery: bg,
		grid: Ig,
		home: Dg,
		inverter: Tg,
		ev: Eg,
		backup: Og,
		meter: Mg,
		fault: yg,
		ok: xg,
		lock: jg,
		settings: wg,
		temperature: Fg,
		clock: Cg,
		power: Ng,
		info: kg,
		busy: Ag,
		expand: Sg
	};
})), Bg, V = t((() => {
	D(), zg(), Bg = class extends E {
		static {
			this.properties = { name: { type: String } };
		}
		static {
			this.styles = d`
        :host {
            display: inline-flex;
            width: var(--saj-icon-size, 24px);
            height: var(--saj-icon-size, 24px);
            fill: currentcolor;
        }
        svg {
            width: 100%;
            height: 100%;
        }
    `;
		}
		constructor() {
			super(), this.name = "info";
		}
		render() {
			return S`<svg viewBox="0 0 24 24" aria-hidden="true"><path d=${Rg[this.name]}></path></svg>`;
		}
	}, customElements.define("saj-icon", Bg);
})), Vg, Hg = t((() => {
	N(), Vg = class {
		constructor() {
			this.entityIds = [];
		}
		needed({ previous: e, next: t, deviceId: n }) {
			return e.entities !== t.entities || e.devices !== t.devices || e.language !== t.language || e.locale !== t.locale || this.idsOf({
				hass: t,
				deviceId: n
			}).some((n) => e.states[n] !== t.states[n]);
		}
		idsOf({ hass: e, deviceId: t }) {
			return (this.registry !== e.entities || this.cachedDeviceId !== t) && (this.registry = e.entities, this.cachedDeviceId = t, this.entityIds = t === void 0 ? [] : rg({
				hass: e,
				deviceId: t
			})), this.entityIds;
		}
	};
})), H, Ug = t((() => {
	D(), Zh(), H = class extends E {
		static {
			this.properties = { hass: { attribute: !1 } };
		}
		get text() {
			return Jh(this.hass?.language ?? "en");
		}
	};
})), U, Wg = t((() => {
	Hg(), Ug(), U = class extends H {
		constructor(...e) {
			super(...e), this.redraw = new Vg();
		}
		shouldUpdate(e) {
			let t = e.get("hass"), { hass: n } = this;
			return e.size !== 1 || t === void 0 || n === void 0 || this.redraw.needed({
				previous: t,
				next: n,
				deviceId: this.watchedDeviceId()
			});
		}
	};
})), Gg, W, G, K = t((() => {
	D(), Gg = {
		primary: "var(--primary-color, #03a9f4)",
		secondary: "var(--secondary-text-color, #727272)",
		disabled: "var(--disabled-text-color, #bdbdbd)",
		warning: "var(--warning-color, #ff9800)",
		error: "var(--error-color, #db4437)",
		success: "var(--success-color, #43a047)"
	}, W = (e) => e === void 0 ? "inherit" : Gg[e], G = d`
    :host {
        display: block;
        color: var(--primary-text-color, #212121);
        font-family: var(--primary-font-family, sans-serif);
    }
    button {
        font: inherit;
        color: inherit;
    }
    button:focus-visible,
    input:focus-visible,
    select:focus-visible {
        outline: 2px solid var(--primary-color, #03a9f4);
        outline-offset: 2px;
    }
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition: none !important;
        }
    }
`;
})), Kg = /* @__PURE__ */ n({ SajStatusBadge: () => Xg }), qg, Jg, Yg, Xg, Zg = t((() => {
	D(), at(), dt(), L(), z(), N(), hg(), vg(), V(), Wg(), K(), qg = "saj-local-status-badge", Jg = `custom:${qg}`, Yg = "operating_mode", Xg = class extends U {
		static {
			this.properties = {
				...U.properties,
				config: { attribute: !1 }
			};
		}
		static {
			this.styles = [G, d`
            :host {
                display: inline-block;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                box-sizing: border-box;
                height: var(--ha-badge-size, 36px);
                padding: 0 12px;
                background: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                border-width: var(--ha-card-border-width, 1px);
                border-style: solid;
                border-color: var(
                    --ha-card-border-color,
                    var(--divider-color, #e0e0e0)
                );
                border-radius: var(--ha-badge-border-radius, 18px);
                box-shadow: var(--ha-card-box-shadow, none);
                font-size: 0.9rem;
            }
            button.badge {
                cursor: pointer;
            }
            .dimmed {
                opacity: 0.5;
            }
        `];
		}
		static getConfigForm() {
			return F(() => []);
		}
		static getStubConfig(e) {
			return {
				type: Jg,
				device: ng(e)[0]?.id
			};
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			return this.config?.device;
		}
		render() {
			let { hass: e, config: t, text: n } = this, r = e === void 0 || t?.device === void 0 ? void 0 : k({
				hass: e,
				deviceId: t.device
			});
			if (e === void 0 || r === void 0 || r.size === 0) return x`<div class="badge dimmed">
                ${n("choose_system")}
            </div>`;
			let i = r.get(Yg), a = [i, ...B.map((e) => r.get(e.summaryKey))].filter((e) => e !== void 0), o = !ag(a), s = mg(r).length, c = o ? i === void 0 ? "" : e.formatEntityState(i.state) : n("not_answering"), l = x`<saj-icon name="inverter"></saj-icon>
            <span
                class="state"
                style=${rt({ color: W(_g(i?.state.state)) })}
                >${c}</span
            >
            ${o && s > 0 ? x`<span
                          class="faults"
                          style=${rt({ color: W("error") })}
                          >${n("faults_count", { count: s })}</span
                      >` : w}`;
			return i === void 0 ? x`<div class="badge">${l}</div>` : x`<button
                  type="button"
                  class=${o ? "badge" : "badge dimmed"}
                  @click=${() => {
				lt({
					host: this,
					entityId: i.entityId
				});
			}}
              >
                  ${l}
              </button>`;
		}
	}, customElements.define(qg, Xg), lg({
		type: qg,
		nameKey: "badge_name",
		descriptionKey: "badge_description"
	});
})), Qg, $g, e_, t_, n_, r_, i_, a_, o_, s_ = t((() => {
	N(), Qg = .8, $g = 1e4, e_ = {
		state: "idle",
		line: "none"
	}, t_ = {
		solar: {
			positive: {
				state: "producing",
				line: "to_inverter"
			},
			negative: {
				state: "producing",
				line: "to_inverter"
			}
		},
		battery: {
			positive: {
				state: "discharging",
				line: "to_inverter"
			},
			negative: {
				state: "charging",
				line: "from_inverter"
			}
		},
		grid: {
			positive: {
				state: "exporting",
				line: "from_inverter"
			},
			negative: {
				state: "importing",
				line: "to_inverter"
			}
		},
		consumer: {
			positive: {
				state: "consuming",
				line: "from_inverter"
			},
			negative: {
				state: "consuming",
				line: "from_inverter"
			}
		}
	}, n_ = ({ kind: e, watts: t }) => {
		if (Math.abs(t) <= 10) return e_;
		let n = t_[e];
		return t > 0 ? n.positive : n.negative;
	}, r_ = (e) => {
		let t = Math.log10(10), n = Math.log10($g), r = (Math.log10(Math.max(Math.abs(e), 10)) - t) / (n - t);
		return Math.max(Qg, 6 - 5.2 * Math.min(r, 1));
	}, i_ = /* @__PURE__ */ new Map([
		["W", 1],
		["kW", 1e3],
		["MW", 1e6]
	]), a_ = (e) => {
		let t = j(e);
		if (t === null) return null;
		let n = e.state.attributes.unit_of_measurement;
		return t * ((typeof n == "string" ? i_.get(n) : 1) ?? 1);
	}, o_ = {
		charging: "charging",
		discharging: "discharging",
		importing: "importing",
		exporting: "exporting",
		idle: "idle"
	};
})), c_, l_, u_, d_, f_, p_, m_, h_ = t((() => {
	D(), K(), c_ = 360, l_ = -90, u_ = 100, d_ = (e) => Math.min(Math.max(e, 0), u_), f_ = (e) => {
		let t = (l_ + d_(e) / u_ * c_) * Math.PI / (c_ / 2), n = (e) => ({
			x: 50 + e * Math.cos(t),
			y: 50 + e * Math.sin(t)
		}), r = n(35), i = n(49);
		return {
			x1: r.x,
			y1: r.y,
			x2: i.x,
			y2: i.y
		};
	}, p_ = (e) => 2 * Math.PI * 42 * d_(e) / u_, m_ = class extends E {
		static {
			this.properties = {
				percent: { type: Number },
				displayValue: { type: String },
				caption: { type: String },
				label: { type: String },
				tone: { type: String },
				markers: { attribute: !1 }
			};
		}
		static {
			this.styles = [G, d`
            :host {
                display: inline-block;
                width: 100%;
                max-width: 220px;
            }
            .track {
                stroke: var(--divider-color, #e0e0e0);
            }
            .centre-value {
                font-size: 18px;
                font-weight: 500;
                fill: var(--primary-text-color, #212121);
            }
            .centre-caption {
                font-size: 8px;
                fill: var(--secondary-text-color, #727272);
            }
            .marker {
                stroke: var(--primary-text-color, #212121);
                stroke-width: 2;
            }
        `];
		}
		constructor() {
			super(), this.percent = 0, this.displayValue = "", this.caption = "", this.label = "", this.tone = "primary", this.markers = [];
		}
		render() {
			let e = 2 * Math.PI * 42;
			return x`<svg
            viewBox="0 0 100 100"
            role="img"
            aria-label=${`${this.label} ${this.displayValue}`.trim()}
        >
            ${S`<circle class="track" cx=${50} cy=${50} r=${42} fill="none" stroke-width=${8}></circle>
            <circle
                cx=${50}
                cy=${50}
                r=${42}
                fill="none"
                stroke-width=${8}
                stroke-linecap="round"
                stroke=${W(this.tone)}
                stroke-dasharray="${p_(this.percent)} ${e}"
                transform="rotate(-90 ${50} ${50})"
            ></circle>
            ${this.markers.map((e) => {
				let t = f_(e.percent);
				return S`<line class="marker" x1=${t.x1} y1=${t.y1} x2=${t.x2} y2=${t.y2}><title>${e.label}</title></line>`;
			})}
            <text class="centre-value" x=${50} y=${52} text-anchor="middle">${this.displayValue}</text>
            <text class="centre-caption" x=${50} y=${64} text-anchor="middle">${this.caption}</text>`}
        </svg>`;
		}
	}, customElements.define("saj-ring-gauge", m_);
})), g_, __ = t((() => {
	D(), K(), g_ = class extends E {
		static {
			this.properties = { heading: { type: String } };
		}
		static {
			this.styles = [G, d`
            .card {
                box-sizing: border-box;
                height: 100%;
                padding: 16px;
                background: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                border-radius: var(--ha-card-border-radius, 12px);
                border-width: var(--ha-card-border-width, 1px);
                border-style: solid;
                border-color: var(
                    --ha-card-border-color,
                    var(--divider-color, #e0e0e0)
                );
                box-shadow: var(--ha-card-box-shadow, none);
            }
            h2 {
                margin: 0 0 12px;
                font-size: 1.1rem;
                font-weight: 500;
            }
        `];
		}
		constructor() {
			super(), this.heading = "";
		}
		render() {
			return x`<div class="card">
            ${this.heading === "" ? w : x`<h2>${this.heading}</h2>`}
            <slot></slot>
        </div>`;
		}
	}, customElements.define("saj-card", g_);
})), v_, y_ = t((() => {
	D(), dt(), V(), Ug(), K(), v_ = class extends H {
		static {
			this.properties = {
				...H.properties,
				locked: { type: Boolean },
				kind: { type: String },
				deviceId: { type: String },
				message: { type: String }
			};
		}
		static {
			this.styles = [G, d`
            .empty {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
                padding: 8px 0;
            }
            .title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 500;
            }
            .body {
                color: var(--secondary-text-color, #727272);
            }
            button {
                padding: 0;
                background: none;
                border: none;
                color: var(--primary-color, #03a9f4);
                cursor: pointer;
            }
        `];
		}
		constructor() {
			super(), this.locked = !1, this.kind = "", this.message = "";
		}
		render() {
			let { text: e } = this;
			return this.locked ? x`<div class="empty">
                  <span class="title"
                      ><saj-icon name="lock"></saj-icon>${e("locked_message")}</span
                  >
                  ${this.renderLink({
				label: e("open_settings"),
				path: st
			})}
              </div>` : x`<div class="empty">
                  <span class="title">${e("empty_title")}</span>
                  <span class="body"
                      >${this.message === "" ? e("empty_enable", { kind: this.kind }) : this.message}</span
                  >
                  ${this.deviceId === void 0 ? w : this.renderLink({
				label: e("open_device_page"),
				path: ct(this.deviceId)
			})}
              </div>`;
		}
		renderLink({ label: e, path: t }) {
			return x`<button
            type="button"
            @click=${() => {
				ut({
					host: this,
					path: t
				});
			}}
        >
            ${e}
        </button>`;
		}
	}, customElements.define("saj-empty-state", v_);
})), b_, x_, S_ = t((() => {
	D(), V(), K(), b_ = {
		primary: "info",
		warning: "info",
		error: "fault"
	}, x_ = class extends E {
		static {
			this.properties = {
				message: { type: String },
				tone: { type: String }
			};
		}
		static {
			this.styles = [G, d`
            .notice {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 0;
            }
            .message {
                flex: 1;
            }
        `];
		}
		constructor() {
			super(), this.message = "", this.tone = "primary";
		}
		render() {
			return x`<div
            class="notice"
            role=${this.tone === "error" ? "alert" : "status"}
        >
            <saj-icon
                .name=${b_[this.tone]}
                style="color: ${W(this.tone)}"
            ></saj-icon>
            <span class="message">${this.message}</span>
            <slot></slot>
        </div>`;
		}
	}, customElements.define("saj-notice", x_);
})), C_, w_ = t((() => {
	D(), at(), dt(), V(), K(), C_ = class extends E {
		static {
			this.properties = {
				label: { type: String },
				value: { type: String },
				icon: { type: String },
				entityId: { type: String },
				tone: { type: String },
				dimmed: { type: Boolean }
			};
		}
		static {
			this.styles = [G, d`
            .row {
                display: flex;
                align-items: center;
                gap: 8px;
                width: 100%;
                padding: 4px 0;
                background: none;
                border: none;
                text-align: start;
            }
            button.row {
                cursor: pointer;
            }
            .label {
                flex: 1;
                color: var(--secondary-text-color, #727272);
            }
            .dimmed .value {
                opacity: 0.5;
            }
        `];
		}
		constructor() {
			super(), this.label = "", this.value = "", this.dimmed = !1;
		}
		render() {
			let e = x`${this.icon === void 0 ? w : x`<saj-icon .name=${this.icon}></saj-icon>`}
            <span class="label">${this.label}</span>
            <span
                class="value"
                style=${rt({ color: W(this.tone) })}
                >${this.value}</span
            >`, t = this.dimmed ? "row dimmed" : "row", { entityId: n } = this;
			return n === void 0 ? x`<div class=${t}>${e}</div>` : x`<button
                  type="button"
                  class=${t}
                  @click=${() => {
				lt({
					host: this,
					entityId: n
				});
			}}
              >
                  ${e}
              </button>`;
		}
	}, customElements.define("saj-value-row", C_);
})), T_, E_, D_, O_, k_, A_, j_, M_, N_, P_, F_, q = t((() => {
	N(), T_ = 1500, E_ = (e) => {
		let t = e.get("control_allowed") ?? null;
		return {
			locked: t?.state.state === "off",
			entity: t
		};
	}, D_ = (e) => ({
		domain: "number",
		service: "set_value",
		data: { value: e }
	}), O_ = (e) => ({
		domain: "select",
		service: "select_option",
		data: { option: e }
	}), k_ = (e) => ({
		domain: "time",
		service: "set_value",
		data: { time: e }
	}), A_ = (e) => ({
		domain: "switch",
		service: e ? "turn_on" : "turn_off"
	}), j_ = () => ({
		domain: "button",
		service: "press"
	}), M_ = (e) => `component.${Qh}.exceptions.${e}.message`, N_ = async ({ hass: e, error: t }) => {
		let n = t ?? {}, r = n.message ?? String(t);
		if (n.translation_domain !== "saj_local" || n.translation_key === void 0) return r;
		let i = (await e.loadBackendTranslation("exceptions", Qh))(M_(n.translation_key), n.translation_placeholders);
		return i === "" ? r : i;
	}, P_ = class {
		constructor(e, t) {
			this.host = e, this.hassProvider = t, this.busyEntities = /* @__PURE__ */ new Set(), this.errors = /* @__PURE__ */ new Map();
		}
		isBusy(e) {
			return this.busyEntities.has(e);
		}
		errorOf(e) {
			return this.errors.get(e) ?? null;
		}
		async submit({ entityId: e, request: t }) {
			let n = this.hassProvider();
			if (!(n === void 0 || this.busyEntities.has(e))) {
				this.errors.delete(e), this.busyEntities.add(e), this.host.requestUpdate();
				try {
					await n.callService(t.domain, t.service, t.data, { entity_id: e });
				} catch (t) {
					this.errors.set(e, await N_({
						hass: n,
						error: t
					}));
				} finally {
					this.busyEntities.delete(e), this.host.requestUpdate();
				}
			}
		}
	}, F_ = class {
		constructor(e) {
			this.options = e, this.pending = null, this.timer = null;
		}
		push(e) {
			this.pending = { value: e }, this.stopTimer(), this.timer = setTimeout(() => {
				this.flush();
			}, this.options.delayMilliseconds);
		}
		flush() {
			this.stopTimer();
			let { pending: e } = this;
			this.pending = null, e !== null && this.options.commit(e.value);
		}
		cancel() {
			this.stopTimer(), this.pending = null;
		}
		stopTimer() {
			this.timer !== null && (clearTimeout(this.timer), this.timer = null);
		}
	};
})), I_, L_, R_, z_, B_, V_ = t((() => {
	N(), I_ = " ", L_ = " - ", R_ = (e) => [e.name_by_user ?? e.name ?? "", e.model ?? ""].filter((e) => e !== "").join(I_), z_ = (e) => {
		let t = ng(e).map((e) => ({
			device: e,
			base: R_(e)
		}));
		return new Map(t.map(({ device: e, base: n }) => {
			let r = t.filter((e) => e.base === n).length > 1, i = e.serial_number ?? "";
			return [e.id, r && i !== "" ? `${n}${L_}${i}` : n];
		}));
	}, B_ = ({ hass: e, deviceId: t }) => z_(e).get(t) ?? "";
})), H_, U_, J, W_, Y, X = t((() => {
	D(), __(), y_(), S_(), w_(), Wg(), N(), q(), V_(), H_ = "opacity: 0.5", U_ = [{ type: "entity" }], J = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [n];
	}), W_ = ({ name: e, options: t }) => ({
		name: e,
		default: t.map((e) => e.value),
		selector: { select: {
			options: t,
			multiple: !0,
			mode: "list"
		} }
	}), Y = class extends U {
		constructor(...e) {
			super(...e), this.hasControls = !1, this.entityKindKey = "entity_kind_reading", this.tracker = new P_(this, () => this.hass);
		}
		static {
			this.properties = {
				...U.properties,
				config: {
					attribute: !1,
					state: !0
				}
			};
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			return this.config?.device;
		}
		getCardSize() {
			return this.cardRows;
		}
		getGridOptions() {
			return {
				columns: 12,
				min_columns: 6
			};
		}
		nameOf({ context: e, entity: t }) {
			return e.hass.formatEntityName(t.state, U_);
		}
		valueText({ context: e, entity: t, absolute: n = !1 }) {
			if (A(t)) return this.text("unavailable");
			let r = n ? j(t) : null;
			return e.hass.formatEntityState(t.state, r === null ? void 0 : String(Math.abs(r)));
		}
		valueRow({ context: e, entity: t, icon: n, tone: r, absolute: i, label: a, value: o }) {
			return x`<saj-value-row
            .label=${a ?? this.nameOf({
				context: e,
				entity: t
			})}
            .value=${o ?? this.valueText({
				context: e,
				entity: t,
				absolute: i
			})}
            .icon=${n}
            .tone=${r}
            .entityId=${t.entityId}
            .dimmed=${e.dimmed}
        ></saj-value-row>`;
		}
		renderEmpty(e) {
			return x`<saj-empty-state
            .hass=${this.hass}
            .locked=${this.hasControls && e.lock.locked}
            .kind=${this.text(this.entityKindKey)}
            .message=${this.emptyMessage?.(e) ?? ""}
            .deviceId=${e.deviceId}
        ></saj-empty-state>`;
		}
		renderLockedBanner(e) {
			return e.lock.locked ? x`<saj-empty-state
                  .hass=${this.hass}
                  .locked=${!0}
              ></saj-empty-state>` : w;
		}
		dimmedBody({ context: e, content: t }) {
			return x`<div style=${e.dimmed ? H_ : ""}>
            ${t}
        </div>`;
		}
		render() {
			let { hass: e, config: t } = this;
			if (e === void 0 || t === void 0) return w;
			let { device: n } = t, r = n === void 0 ? /* @__PURE__ */ new Map() : k({
				hass: e,
				deviceId: n
			}), i = n === void 0 ? "" : B_({
				hass: e,
				deviceId: n
			});
			return x`<saj-card .heading=${i}
            >${n === void 0 || r.size === 0 ? x`<saj-notice
                          .message=${this.text("choose_system")}
                      ></saj-notice>` : this.renderSystem({
				hass: e,
				deviceId: n,
				entities: r
			})}</saj-card
        >`;
		}
		renderSystem({ hass: e, deviceId: t, entities: n }) {
			let r = this.shownEntities(n), i = {
				hass: e,
				deviceId: t,
				entities: n,
				lock: E_(n),
				tracker: this.tracker,
				dimmed: ag(r)
			};
			return r.length === 0 ? this.renderEmpty(i) : x`${i.dimmed ? x`<saj-notice
                      tone="warning"
                      .message=${this.text("not_answering")}
                  ></saj-notice>` : w}${this.renderBody(i)}`;
		}
	};
})), G_ = /* @__PURE__ */ n({
	BATTERY_CARD_TYPE: () => K_,
	SajLocalBatteryCard: () => sv
}), K_, q_, J_, Y_, X_, Z_, Q_, $_, ev, tv, nv, rv, iv, av, ov, sv, cv = t((() => {
	D(), dt(), z(), N(), s_(), h_(), K(), L(), X(), K_ = "saj-local-battery-card", q_ = 5, J_ = !0, Y_ = "battery_soc", X_ = "battery_power", Z_ = " · ", Q_ = ["battery_time_to_full", "battery_time_to_empty"], $_ = {
		charging: "battery_time_to_full",
		discharging: "battery_time_to_empty"
	}, ev = [
		"backup_reserve_soc",
		"battery_charge_soc_limit",
		"battery_discharge_soc_limit_on_grid"
	], tv = [
		{
			key: "battery_voltage",
			icon: "battery"
		},
		{
			key: "battery_current",
			icon: "battery"
		},
		{
			key: "battery_temperature",
			icon: "temperature"
		},
		{
			key: "battery_usable_capacity",
			icon: "battery"
		}
	], nv = [
		{
			key: "soc",
			icon: "battery"
		},
		{
			key: "soh",
			icon: "battery"
		},
		{
			key: "voltage",
			icon: "battery"
		},
		{
			key: "current",
			icon: "battery"
		},
		{
			key: "temperature",
			icon: "temperature"
		},
		{
			key: "cycles",
			icon: "info"
		}
	], rv = [{
		key: "fault",
		tone: "error"
	}, {
		key: "warning",
		tone: "warning"
	}], iv = /^battery_pack(\d+)_/, av = 10, ov = ({ number: e, field: t }) => `battery_pack${String(e)}_${t}`, sv = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = q_;
		}
		static {
			this.styles = [G, d`
            .gauge {
                display: flex;
                justify-content: center;
                width: 100%;
                padding: 0;
                background: none;
                border: none;
                cursor: pointer;
            }
            h3 {
                display: flex;
                align-items: center;
                gap: 4px;
                margin: 8px 0 0;
                font-size: 1rem;
                font-weight: 500;
            }
        `];
		}
		static getConfigForm() {
			return F(() => [P({
				name: "show_packs",
				fallback: J_
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		get showPacks() {
			return this.config?.show_packs ?? J_;
		}
		packNumbers(e) {
			let t = /* @__PURE__ */ new Set();
			for (let n of e.keys()) {
				let e = iv.exec(n);
				e?.[1] !== void 0 && t.add(Number.parseInt(e[1], av));
			}
			return [...t].sort((e, t) => e - t);
		}
		packEntities({ entities: e, number: t }) {
			return J({
				entities: e,
				keys: [...nv, ...rv].map(({ key: e }) => ov({
					number: t,
					field: e
				}))
			});
		}
		shownEntities(e) {
			if (!e.has(Y_)) return [];
			let t = [
				Y_,
				...ev,
				X_,
				...Q_,
				...tv.map(({ key: e }) => e)
			], n = J({
				entities: e,
				keys: t
			}), r = this.showPacks ? this.packNumbers(e).flatMap((t) => this.packEntities({
				entities: e,
				number: t
			})) : [];
			return [...n, ...r];
		}
		renderEmpty() {
			return x`<saj-notice
            .message=${this.text("no_battery")}
        ></saj-notice>`;
		}
		renderBody(e) {
			let { entities: t } = e;
			return x`${J({
				entities: t,
				keys: [Y_]
			}).map((t) => this.renderGauge({
				context: e,
				soc: t
			}))}
        ${J({
				entities: t,
				keys: [X_]
			}).map((t) => this.renderPower({
				context: e,
				power: t
			}))}
        ${this.renderEstimate(e)}
        ${tv.map(({ key: n, icon: r }) => J({
				entities: t,
				keys: [n]
			}).map((t) => this.valueRow({
				context: e,
				entity: t,
				icon: r
			})))}
        ${this.showPacks ? this.packNumbers(t).map((t) => this.renderPack({
				context: e,
				number: t
			})) : w}`;
		}
		renderGauge({ context: e, soc: t }) {
			let n = ev.flatMap((t) => {
				let n = e.entities.get(t), r = n === void 0 ? null : j(n);
				return n === void 0 || r === null ? [] : [{
					percent: r,
					label: `${this.nameOf({
						context: e,
						entity: n
					})} ${this.valueText({
						context: e,
						entity: n
					})}`
				}];
			}), r = this.nameOf({
				context: e,
				entity: t
			}), i = this.valueText({
				context: e,
				entity: t
			});
			return x`<button
            type="button"
            class="gauge"
            aria-label=${`${r} ${i}`}
            @click=${() => {
				lt({
					host: this,
					entityId: t.entityId
				});
			}}
        >
            <saj-ring-gauge
                .percent=${j(t) ?? 0}
                .displayValue=${i}
                .label=${r}
                .tone=${A(t) ? "disabled" : "primary"}
                .markers=${n}
                style=${e.dimmed ? "opacity: 0.5" : ""}
            ></saj-ring-gauge>
        </button>`;
		}
		renderPower({ context: e, power: t }) {
			let n = a_(t), r = n === null ? void 0 : o_[n_({
				kind: "battery",
				watts: n
			}).state], i = [this.valueText({
				context: e,
				entity: t,
				absolute: !0
			}), ...r === void 0 ? [] : [this.text(r)]].join(Z_);
			return this.valueRow({
				context: e,
				entity: t,
				icon: "battery",
				value: i
			});
		}
		renderEstimate(e) {
			let t = e.entities.get(X_), n = t === void 0 ? null : a_(t), r = n === null ? void 0 : $_[n_({
				kind: "battery",
				watts: n
			}).state], i = r === void 0 ? void 0 : e.entities.get(r);
			return i === void 0 ? w : this.valueRow({
				context: e,
				entity: i,
				icon: "battery"
			});
		}
		renderPack({ context: e, number: t }) {
			let { entities: n } = e;
			return x`<h3>
                ${this.text("battery_pack", { number: t })}${rv.map(({ key: r, tone: i }) => {
				let a = n.get(ov({
					number: t,
					field: r
				}));
				return a !== void 0 && M(a) ? x`<saj-icon
                                  name="fault"
                                  role="img"
                                  aria-label=${this.nameOf({
					context: e,
					entity: a
				})}
                                  style="color: ${W(i)}"
                              ></saj-icon>` : w;
			})}
            </h3>
            ${nv.map(({ key: r, icon: i }) => {
				let a = n.get(ov({
					number: t,
					field: r
				}));
				return a === void 0 ? w : this.valueRow({
					context: e,
					entity: a,
					icon: i
				});
			})}`;
		}
	}, customElements.define(K_, sv), R({
		type: K_,
		nameKey: "battery_card_name",
		descriptionKey: "battery_card_description",
		preview: !0
	});
})), lv, uv, Z, Q = t((() => {
	D(), V(), Ug(), K(), lv = "saj-commit", uv = [G, d`
        .control {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 0;
        }
        .label {
            flex: 1;
            color: var(--secondary-text-color, #727272);
        }
        .input {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .busy {
            --saj-icon-size: 18px;
            animation: spin 1s linear infinite;
        }
        .error {
            color: var(--error-color, #db4437);
            font-size: 0.85rem;
        }
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
    `], Z = class extends H {
		static {
			this.properties = {
				...H.properties,
				label: { type: String },
				labelHidden: { type: Boolean },
				disabled: { type: Boolean },
				busy: { type: Boolean },
				error: { type: String }
			};
		}
		static {
			this.styles = uv;
		}
		constructor() {
			super(), this.label = "", this.labelHidden = !1, this.disabled = !1, this.busy = !1, this.error = "";
		}
		get inactive() {
			return this.disabled || this.busy;
		}
		commit(e) {
			this.dispatchEvent(new CustomEvent(lv, {
				detail: e,
				bubbles: !0,
				composed: !0
			}));
		}
		renderFrame(e) {
			return x`<div class="control">
                ${this.label === "" || this.labelHidden ? w : x`<span class="label">${this.label}</span>`}
                <span class="input"
                    >${e}${this.busy ? x`<saj-icon
                                  class="busy"
                                  name="busy"
                                  role="status"
                                  aria-label=${this.text("busy")}
                              ></saj-icon>` : w}</span
                >
            </div>
            ${this.error === "" ? w : x`<div class="error" role="alert">${this.error}</div>`}`;
		}
	};
})), dv = /* @__PURE__ */ n({
	FAULTS_CARD_TYPE: () => fv,
	SajLocalFaultsCard: () => _v
}), fv, pv, mv, hv, gv, _v, vv = t((() => {
	D(), Zh(), z(), q(), hg(), Q(), L(), X(), fv = "saj-local-faults-card", pv = 4, mv = !0, hv = "clear_current_fault", gv = {
		inverter: "inverter",
		battery: "battery",
		ev: "ev_charger"
	}, _v = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = pv, this.hasControls = !0;
		}
		static {
			this.styles = [...uv, d`
            h3 {
                margin: 8px 0 0;
                font-size: 1rem;
                font-weight: 500;
            }
            .hint {
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
            .clear {
                padding: 6px 12px;
                background: none;
                border: 1px solid var(--divider-color, #e0e0e0);
                border-radius: 8px;
                cursor: pointer;
            }
            .clear:disabled {
                opacity: 0.5;
                cursor: default;
            }
        `];
		}
		static getConfigForm() {
			return F(() => [P({
				name: "show_groups_without_faults",
				fallback: mv
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		shownEntities(e) {
			return pg(e).map(({ summary: e }) => e);
		}
		renderBody(e) {
			let t = this.config?.show_groups_without_faults ?? mv, n = pg(e.entities).filter(({ active: e }) => e || t), r = e.entities.has(hv);
			return x`${r ? this.renderLockedBanner(e) : w}${n.map((t) => this.renderGroup({
				context: e,
				group: t
			}))}`;
		}
		renderGroup({ context: e, group: t }) {
			let n = this.text(gv[t.id]);
			return t.active ? x`<h3>${n}</h3>
            ${t.rows.map((t) => this.renderRow({
				context: e,
				row: t
			}))}
            ${t.id === "inverter" ? this.renderClear(e) : w}` : x`<saj-value-row
                .label=${n}
                .value=${this.text("no_active_faults")}
                .icon=${"ok"}
                .tone=${"success"}
                .entityId=${t.summary.entityId}
                .dimmed=${e.dimmed}
            ></saj-value-row>`;
		}
		renderRow({ context: e, row: t }) {
			let n = Xh({
				from: t.since,
				now: /* @__PURE__ */ new Date(),
				language: e.hass.language
			});
			return x`${this.valueRow({
				context: e,
				entity: t.entity,
				icon: "fault",
				tone: "error",
				value: n
			})}${t.unrecognised ? x`<div class="hint">${this.text("see_diagnostics")}</div>` : w}`;
		}
		renderClear(e) {
			let t = e.entities.get(hv);
			if (t === void 0) return w;
			let n = this.tracker.isBusy(t.entityId), r = this.tracker.errorOf(t.entityId);
			return x`<div class="control">
                <button
                    type="button"
                    class="clear"
                    ?disabled=${e.lock.locked || n}
                    @click=${() => {
				this.tracker.submit({
					entityId: t.entityId,
					request: j_()
				});
			}}
                >
                    ${this.text("clear_fault")}
                </button>
                ${n ? x`<saj-icon
                              class="busy"
                              name="busy"
                              role="status"
                              aria-label=${this.text("busy")}
                          ></saj-icon>` : w}
            </div>
            ${r === null ? w : x`<div class="error" role="alert">${r}</div>`}`;
		}
	}, customElements.define(fv, _v), R({
		type: fv,
		nameKey: "faults_card_name",
		descriptionKey: "faults_card_description",
		preview: !0
	});
})), yv = /* @__PURE__ */ n({
	POWER_FLOW_CARD_TYPE: () => bv,
	POWER_FLOW_SCOPES: () => Tv,
	SajLocalPowerFlowCard: () => qv,
	VIEW_HEIGHT: () => 520,
	VIEW_WIDTH: () => 400
}), bv, xv, Sv, Cv, wv, Tv, Ev, Dv, Ov, kv, Av, jv, Mv, Nv, Pv, Fv, Iv, Lv, Rv, zv, Bv, Vv, Hv, Uv, Wv, Gv, Kv, qv, Jv = t((() => {
	D(), dt(), z(), vg(), s_(), zg(), K(), L(), X(), bv = "saj-local-power-flow-card", xv = 6, Sv = !1, Cv = !0, wv = "system", Tv = ["system", "parallel"], Ev = 104, Dv = 84, Ov = 12, kv = 24, Av = -38, jv = 8, Mv = 22, Nv = 35, Pv = 16, Fv = 16, Iv = " · ", Lv = 460, Rv = {
		x: 200,
		y: 225
	}, zv = {
		x: 200,
		y: 50
	}, Bv = [
		{
			id: "solar",
			labelKey: "solar",
			icon: "solar",
			kind: "solar",
			keys: {
				system: "pv_power",
				parallel: "parallel_pv_power"
			},
			flowWords: !1,
			absolute: !1,
			optional: !1,
			position: zv
		},
		{
			id: "battery",
			labelKey: "battery",
			icon: "battery",
			kind: "battery",
			keys: {
				system: "battery_power",
				parallel: "parallel_battery_power"
			},
			secondaryKeys: {
				system: "battery_soc",
				parallel: "parallel_battery_soc"
			},
			flowWords: !0,
			absolute: !0,
			optional: !1,
			position: {
				x: 200,
				y: 360
			}
		},
		{
			id: "grid",
			labelKey: "grid",
			icon: "grid",
			kind: "grid",
			keys: {
				system: "grid_power",
				parallel: "parallel_grid_power"
			},
			flowWords: !0,
			absolute: !0,
			optional: !1,
			position: {
				x: 60,
				y: 225
			}
		},
		{
			id: "home",
			labelKey: "home",
			icon: "home",
			kind: "consumer",
			keys: {
				system: "load_power",
				parallel: "parallel_load_power"
			},
			flowWords: !1,
			absolute: !1,
			optional: !1,
			position: {
				x: 340,
				y: 225
			}
		},
		{
			id: "ev",
			labelKey: "ev_charger",
			icon: "ev",
			kind: "consumer",
			keys: {
				system: "ev_power",
				parallel: "ev_power"
			},
			secondaryKeys: {
				system: "ev_status",
				parallel: "ev_status"
			},
			flowWords: !1,
			absolute: !1,
			optional: !0
		},
		{
			id: "backup",
			labelKey: "backup_load",
			icon: "backup",
			kind: "consumer",
			keys: {
				system: "backup_load_power",
				parallel: "parallel_backup_load_power"
			},
			flowWords: !1,
			absolute: !1,
			optional: !0
		},
		{
			id: "meter",
			labelKey: "meter_b",
			icon: "meter",
			kind: null,
			keys: {
				system: "meter_b_power",
				parallel: "parallel_meter_b_power"
			},
			flowWords: !1,
			absolute: !1,
			optional: !0
		}
	], Vv = "operating_mode", Hv = /^pv([1-9]\d*)_power$/, Uv = /\D/g, Wv = {
		idle: "var(--divider-color, #e0e0e0)",
		producing: "var(--energy-solar-color, #ff9800)",
		consuming: "var(--primary-color, #03a9f4)",
		charging: "var(--energy-battery-in-color, #f06292)",
		discharging: "var(--energy-battery-out-color, #4db6ac)",
		importing: "var(--energy-grid-consumption-color, #488fc2)",
		exporting: "var(--energy-grid-return-color, #8353d1)"
	}, Gv = {
		state: "idle",
		line: "none"
	}, Kv = (e) => e.key === "Enter" || e.key === " ", qv = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = xv;
		}
		static {
			this.styles = [G, d`
            svg {
                display: block;
                width: 100%;
                height: auto;
            }
            .node {
                cursor: pointer;
            }
            .node:focus-visible {
                outline: 2px solid var(--primary-color, #03a9f4);
            }
            .box {
                fill: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                stroke: var(--divider-color, #e0e0e0);
            }
            .icon {
                fill: var(--primary-text-color, #212121);
            }
            .value {
                font-size: 15px;
                font-weight: 500;
                fill: var(--primary-text-color, #212121);
            }
            .label,
            .secondary,
            .string {
                font-size: 11px;
                fill: var(--secondary-text-color, #727272);
            }
            .string {
                paint-order: stroke;
                stroke: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                stroke-width: 4px;
            }
            .dimmed .value,
            .dimmed .secondary,
            .dimmed .string {
                opacity: 0.5;
            }
            .line {
                fill: none;
                stroke-width: 3;
                stroke-linecap: round;
            }
            .line.idle {
                stroke: var(--divider-color, #e0e0e0);
            }
            .line.active {
                stroke-dasharray: 6 10;
                animation: flow var(--flow-duration, 2s) linear infinite;
            }
            .line.reverse {
                animation-direction: reverse;
            }
            @keyframes flow {
                to {
                    stroke-dashoffset: -16;
                }
            }
        `];
		}
		static getConfigForm() {
			return F((e) => [
				P({
					name: "show_strings",
					fallback: Sv
				}),
				P({
					name: "show_optional_equipment",
					fallback: Cv
				}),
				og({
					name: "scope",
					options: Tv.map((t) => ({
						value: t,
						label: e(`option_scope_${t}`)
					})),
					fallback: wv
				})
			]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				scope: wv
			};
		}
		get scope() {
			return this.config?.scope ?? wv;
		}
		drawnNodes(e) {
			let { scope: t } = this, n = this.config?.show_optional_equipment ?? Cv, r = Bv.flatMap((r) => {
				let i = e.get(r.keys[t]);
				return i === void 0 || r.optional && !n ? [] : [{
					spec: r,
					entity: i
				}];
			}), i = r.filter(({ spec: e }) => e.optional).length, a = 0;
			return r.map(({ spec: n, entity: r }) => {
				let o = a_(r), s = n.secondaryKeys?.[t], c = n.position ?? this.optionalPosition({
					index: a++,
					count: i
				});
				return {
					spec: n,
					entity: r,
					secondaryEntity: s === void 0 ? void 0 : e.get(s),
					watts: o,
					position: c,
					flow: n.kind === null || o === null ? Gv : n_({
						kind: n.kind,
						watts: o
					})
				};
			});
		}
		optionalPosition({ index: e, count: t }) {
			return {
				x: 400 * (e + 1) / (t + 1),
				y: Lv
			};
		}
		stringEntities(e) {
			return this.config?.show_strings ?? Sv ? [...e.values()].filter((e) => Hv.test(e.key)).sort((e, t) => this.stringNumber(e) - this.stringNumber(t)) : [];
		}
		stringNumber(e) {
			return Number(e.key.replace(Uv, ""));
		}
		hasScopedReadings(e) {
			let { scope: t } = this;
			return Bv.some(({ keys: n }) => n.system !== n.parallel && e.has(n[t]));
		}
		shownEntities(e) {
			if (this.scope === "parallel" && !this.hasScopedReadings(e)) return [];
			let t = e.get(Vv);
			return [
				...t === void 0 ? [] : [t],
				...this.drawnNodes(e).map(({ entity: e }) => e),
				...this.stringEntities(e)
			];
		}
		renderBody(e) {
			let t = this.drawnNodes(e.entities), n = e.entities.get(Vv), r = this.stringEntities(e.entities);
			return x`<svg
            class=${e.dimmed ? "dimmed" : ""}
            viewBox="0 0 ${400} ${520}"
            role="group"
        >
            ${t.map((e) => this.renderLine(e))}
            ${t.map((t) => this.renderNode({
				node: t,
				context: e
			}))}
            ${n === void 0 ? w : this.renderHub({
				entity: n,
				context: e
			})}
            ${r.map((t, n) => this.renderString({
				entity: t,
				index: n,
				context: e
			}))}
        </svg>`;
		}
		renderLine(e) {
			let { flow: t, position: n, watts: r } = e, i = t.line !== "none" && r !== null, a = [
				"line",
				i ? "active" : "idle",
				t.line === "from_inverter" ? "reverse" : ""
			].join(" ");
			return S`<line
            class=${a}
            x1=${n.x}
            y1=${n.y}
            x2=${Rv.x}
            y2=${Rv.y}
            style=${i ? `--flow-duration: ${String(r_(r))}s; stroke: ${Wv[t.state]}` : ""}
        ></line>`;
		}
		renderNode({ node: e, context: t }) {
			let { spec: n, entity: r, flow: i, position: a } = e, o = n.flowWords ? o_[i.state] : void 0, s = [...e.secondaryEntity === void 0 ? [] : [this.valueText({
				context: t,
				entity: e.secondaryEntity
			})], ...o === void 0 || e.watts === null ? [] : [this.text(o)]].join(Iv);
			return this.renderTarget({
				entity: r,
				position: a,
				icon: n.icon,
				label: this.text(n.labelKey),
				value: this.valueText({
					context: t,
					entity: r,
					absolute: n.absolute
				}),
				secondary: s
			});
		}
		renderHub({ entity: e, context: t }) {
			return this.renderTarget({
				entity: e,
				position: Rv,
				icon: "inverter",
				label: this.text("inverter"),
				value: this.valueText({
					context: t,
					entity: e
				}),
				secondary: "",
				colour: W(_g(e.state.state))
			});
		}
		renderTarget({ entity: e, position: t, icon: n, label: r, value: i, secondary: a, colour: o }) {
			let { x: s, y: c } = t;
			return this.renderTap({
				entity: e,
				label: `${r} ${i} ${a}`.trim(),
				content: S`<rect
                class="box"
                x=${s - Ev / 2}
                y=${c - Dv / 2}
                width=${Ev}
                height=${Dv}
                rx=${Ov}
            ></rect>
            <path
                class="icon"
                d=${Rg[n]}
                transform="translate(${s - kv / 2} ${c + Av})"
            ></path>
            <text
                class="value"
                x=${s}
                y=${c + jv}
                text-anchor="middle"
                style=${o === void 0 ? "" : `fill: ${o}`}
            >${i}</text>
            <text class="label" x=${s} y=${c + Mv} text-anchor="middle">${r}</text>
            <text class="secondary" x=${s} y=${c + Nv} text-anchor="middle">${a}</text>`
			});
		}
		renderString({ entity: e, index: t, context: n }) {
			let r = `${this.nameOf({
				context: n,
				entity: e
			})}: ${this.valueText({
				context: n,
				entity: e
			})}`;
			return this.renderTap({
				entity: e,
				label: r,
				content: S`<text
                class="string"
                x=${zv.x}
                y=${zv.y + Dv / 2 + Fv + t * Pv}
                text-anchor="middle"
            >${r}</text>`
			});
		}
		renderTap({ entity: e, label: t, content: n }) {
			let r = () => {
				lt({
					host: this,
					entityId: e.entityId
				});
			};
			return S`<g
            class="node"
            role="button"
            tabindex="0"
            aria-label=${t}
            @click=${r}
            @keydown=${(e) => {
				Kv(e) && (e.preventDefault(), r());
			}}
        >${n}</g>`;
		}
	}, customElements.define(bv, qv), R({
		type: bv,
		nameKey: "power_flow_card_name",
		descriptionKey: "power_flow_card_description",
		preview: !0
	});
})), Yv = /* @__PURE__ */ n({
	STATUS_CARD_TYPE: () => Xv,
	SajLocalStatusCard: () => ay
}), Xv, Zv, Qv, $v, ey, ty, ny, ry, iy, ay, oy = t((() => {
	D(), z(), N(), hg(), vg(), K(), L(), X(), Xv = "saj-local-status-card", Zv = 5, Qv = !0, $v = [
		{
			key: "battery_soc",
			icon: "battery"
		},
		{
			key: "inverter_temperature",
			icon: "temperature"
		},
		{
			key: "battery_temperature",
			icon: "temperature"
		},
		{
			key: "off_grid_mode",
			icon: "grid"
		}
	], ey = [
		"pv_energy_today",
		"load_energy_today",
		"grid_import_energy_today",
		"grid_export_energy_today",
		"battery_charge_energy_today",
		"battery_discharge_energy_today"
	], ty = "operating_mode", ny = "application_mode", ry = "application_mode_active", iy = "control_allowed", ay = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = Zv;
		}
		static {
			this.styles = [G, d`
            .section {
                padding: 4px 0;
            }
            .section + .section {
                border-top: 1px solid var(--divider-color, #e0e0e0);
            }
        `];
		}
		static getConfigForm() {
			return F(() => [P({
				name: "show_energy",
				fallback: Qv
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		get showEnergy() {
			return this.config?.show_energy ?? Qv;
		}
		shownEntities(e) {
			return J({
				entities: e,
				keys: [
					ty,
					ny,
					ry,
					...$v.map(({ key: e }) => e),
					...this.showEnergy ? ey : [],
					...B.map(({ summaryKey: e }) => e),
					iy
				]
			});
		}
		renderBody(e) {
			return x`${this.section(this.renderState(e))}${this.section(this.renderMode(e))}${this.section(this.renderReadings(e))}${this.section(this.showEnergy ? this.renderToday(e) : [])}${this.section([...this.renderFaults(e), ...this.renderChanges(e)])}`;
		}
		section(e) {
			return e.length === 0 ? w : x`<div class="section">${e}</div>`;
		}
		renderState(e) {
			let t = e.entities.get(ty);
			return t === void 0 ? [] : [this.valueRow({
				context: e,
				entity: t,
				icon: "inverter",
				tone: _g(t.state.state)
			})];
		}
		renderMode(e) {
			let t = e.entities.get(ny);
			if (t === void 0) return [];
			let n = e.entities.get(ry);
			return [this.valueRow({
				context: e,
				entity: t,
				icon: "settings"
			}), ...n === void 0 || n.state.state === t.state.state ? [] : [this.valueRow({
				context: e,
				entity: n,
				icon: "settings",
				label: this.text("mode_running_now")
			})]];
		}
		renderReadings(e) {
			return $v.flatMap(({ key: t, icon: n }) => {
				let r = e.entities.get(t);
				return r === void 0 ? [] : [this.valueRow({
					context: e,
					entity: r,
					icon: n
				})];
			});
		}
		renderToday(e) {
			return J({
				entities: e.entities,
				keys: ey
			}).map((t) => this.valueRow({
				context: e,
				entity: t,
				icon: "info"
			}));
		}
		renderFaults(e) {
			if (J({
				entities: e.entities,
				keys: B.map(({ summaryKey: e }) => e)
			}).length === 0) return [];
			let t = mg(e.entities), [n] = t, r = t.length;
			return [x`<saj-value-row
                .label=${this.text("faults")}
                .value=${r === 0 ? this.text("no_faults") : this.text("faults_count", { count: r })}
                .icon=${r === 0 ? "ok" : "fault"}
                .tone=${r === 0 ? void 0 : "error"}
                .entityId=${n?.entityId}
                .dimmed=${e.dimmed}
            ></saj-value-row>`];
		}
		renderChanges(e) {
			let t = e.entities.get(iy);
			if (t === void 0) return [];
			let n = M(t);
			return [this.valueRow({
				context: e,
				entity: t,
				icon: "lock",
				label: this.text("changes"),
				tone: n ? "success" : "warning",
				value: A(t) ? this.text("unavailable") : this.text(n ? "changes_allowed" : "changes_off")
			})];
		}
	}, customElements.define(Xv, ay), R({
		type: Xv,
		nameKey: "status_card_name",
		descriptionKey: "status_card_description",
		preview: !0
	});
})), sy, cy = t((() => {
	Ke(), sy = (e) => e ?? w;
})), ly = t((() => {
	cy();
})), uy, dy, fy = t((() => {
	D(), ly(), Q(), uy = ({ mode: e, range: t }) => {
		if (e !== "auto") return e;
		let { min: n, max: r, step: i } = t;
		return n === void 0 || r === void 0 || i === void 0 ? "box" : (r - n) / i <= 256 ? "slider" : "box";
	}, dy = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				value: { type: Number },
				min: { type: Number },
				max: { type: Number },
				step: { type: Number },
				unit: { type: String },
				displayValue: { type: String },
				mode: { type: String },
				draft: { state: !0 }
			};
		}
		constructor() {
			super(), this.onInput = (e) => {
				let t = Number.parseFloat(e.target.value);
				this.draft = Number.isFinite(t) ? t : null;
			}, this.onKeyDown = (e) => {
				e.key === "Enter" && this.onFinish(e);
			}, this.onFinish = (e) => {
				let t = e.target, n = this.draft;
				this.draft = null, t.value = String(this.value), n !== null && this.commit(n);
			}, this.value = 0, this.unit = "", this.displayValue = "", this.mode = "auto", this.draft = null;
		}
		render() {
			let e = uy({
				mode: this.mode,
				range: {
					min: this.min,
					max: this.max,
					step: this.step
				}
			}) === "slider";
			return this.renderFrame(x`<input
                    type=${e ? "range" : "number"}
                    min=${sy(this.min)}
                    max=${sy(this.max)}
                    step=${sy(this.step)}
                    aria-label=${this.label}
                    .value=${e ? this.draftOrValue : String(this.value)}
                    ?disabled=${this.inactive}
                    @input=${this.onInput}
                    @pointerup=${e ? this.onFinish : w}
                    @keydown=${this.onKeyDown}
                    @blur=${this.onFinish}
                />${e ? x`<span class="value"
                              >${this.draft === null ? this.displayValue : `${String(this.draft)} ${this.unit}`}</span
                          >` : x`<span class="unit">${this.unit}</span>`}`);
		}
		get draftOrValue() {
			return String(this.draft ?? this.value);
		}
	}, customElements.define("saj-number-control", dy);
})), py, my = t((() => {
	D(), Q(), py = class extends Z {
		render() {
			return this.renderFrame(x`<button
                type="button"
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @click=${() => {
				this.commit(null);
			}}
            >
                ${this.text("press")}
            </button>`);
		}
	}, customElements.define("saj-press-control", py);
})), hy, gy = t((() => {
	D(), Q(), hy = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				value: { type: String },
				options: { attribute: !1 }
			};
		}
		constructor() {
			super(), this.value = "", this.options = [];
		}
		render() {
			return this.renderFrame(x`<select
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @change=${(e) => {
				let t = e.target, n = t.value;
				t.value = this.value, this.commit(n);
			}}
            >
                ${this.options.map((e) => x`<option
                            value=${e.value}
                            .selected=${e.value === this.value}
                        >
                            ${e.label}
                        </option>`)}
            </select>`);
		}
	}, customElements.define("saj-select-control", hy);
})), _y, vy = t((() => {
	D(), Q(), _y = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				checked: { type: Boolean }
			};
		}
		static {
			this.styles = [...uv, d`
            button {
                position: relative;
                width: 36px;
                height: 20px;
                padding: 0;
                background: var(--disabled-text-color, #bdbdbd);
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }
            button[aria-checked="true"] {
                background: var(--primary-color, #03a9f4);
            }
            button:disabled {
                opacity: 0.5;
                cursor: default;
            }
            .thumb {
                position: absolute;
                top: 2px;
                left: 2px;
                width: 16px;
                height: 16px;
                background: #fff;
                border-radius: 50%;
                transition: transform 0.15s;
            }
            button[aria-checked="true"] .thumb {
                transform: translateX(16px);
            }
        `];
		}
		constructor() {
			super(), this.checked = !1;
		}
		render() {
			return this.renderFrame(x`<button
                type="button"
                role="switch"
                aria-checked=${String(this.checked)}
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @click=${() => {
				this.commit(!this.checked);
			}}
            >
                <span class="thumb"></span>
            </button>`);
		}
	}, customElements.define("saj-switch", _y);
})), yy, by, xy = t((() => {
	D(), Q(), yy = 5, by = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				value: { type: String }
			};
		}
		constructor() {
			super(), this.value = "";
		}
		get shownText() {
			return this.value.slice(0, yy);
		}
		render() {
			return this.renderFrame(x`<input
                type="time"
                aria-label=${this.label}
                .value=${this.shownText}
                ?disabled=${this.inactive}
                @change=${(e) => {
				let t = e.target, n = t.value;
				t.value = this.shownText, n !== "" && this.commit(n);
			}}
            />`);
		}
	}, customElements.define("saj-time-control", by);
})), Sy, Cy, $, wy = t((() => {
	D(), q(), N(), fy(), my(), gy(), vy(), xy(), w_(), Sy = [{ type: "entity" }], Cy = ({ hass: e, entity: t }) => e.formatEntityName(t.state, Sy), $ = ({ context: e, entity: t, labelHidden: n = !1 }) => {
		let { hass: r, lock: i, tracker: a } = e, { attributes: o } = t.state, s = Cy({
			hass: r,
			entity: t
		}), c = i.locked || A(t), l = a.isBusy(t.entityId), u = a.errorOf(t.entityId) ?? "", d = (e) => {
			a.submit({
				entityId: t.entityId,
				request: e
			});
		};
		switch (t.domain) {
			case "number": return x`<saj-number-control
                .hass=${r}
                .label=${s}
                .labelHidden=${n}
                .disabled=${c}
                .busy=${l}
                .error=${u}
                .value=${j(t) ?? 0}
                .min=${o.min}
                .max=${o.max}
                .step=${o.step}
                .unit=${o.unit_of_measurement ?? ""}
                .mode=${o.mode ?? "auto"}
                .displayValue=${r.formatEntityState(t.state)}
                @saj-commit=${(e) => {
				d(D_(e.detail));
			}}
            ></saj-number-control>`;
			case "select": return x`<saj-select-control
                .hass=${r}
                .label=${s}
                .labelHidden=${n}
                .disabled=${c}
                .busy=${l}
                .error=${u}
                .value=${t.state.state}
                .options=${(o.options ?? []).map((e) => ({
				value: e,
				label: r.formatEntityState(t.state, e)
			}))}
                @saj-commit=${(e) => {
				d(O_(e.detail));
			}}
            ></saj-select-control>`;
			case "switch": return x`<saj-switch
                .hass=${r}
                .label=${s}
                .labelHidden=${n}
                .disabled=${c}
                .busy=${l}
                .error=${u}
                .checked=${t.state.state === "on"}
                @saj-commit=${(e) => {
				d(A_(e.detail));
			}}
            ></saj-switch>`;
			case "time": return x`<saj-time-control
                .hass=${r}
                .label=${s}
                .labelHidden=${n}
                .disabled=${c}
                .busy=${l}
                .error=${u}
                .value=${t.state.state}
                @saj-commit=${(e) => {
				d(k_(e.detail));
			}}
            ></saj-time-control>`;
			case "button": return x`<saj-press-control
                .hass=${r}
                .label=${s}
                .labelHidden=${n}
                .disabled=${c}
                .busy=${l}
                .error=${u}
                @saj-commit=${() => {
				d(j_());
			}}
            ></saj-press-control>`;
			default: return x`<saj-value-row
                .label=${s}
                .value=${r.formatEntityState(t.state)}
                .entityId=${t.entityId}
            ></saj-value-row>`;
		}
	};
})), Ty = /* @__PURE__ */ n({
	CONTROLS_CARD_TAG: () => Ey,
	SECTION_IDS: () => Dy,
	SajControlsCard: () => Py
}), Ey, Dy, Oy, ky, Ay, jy, My, Ny, Py, Fy = t((() => {
	D(), z(), N(), X(), K(), L(), wy(), Ey = "saj-local-controls-card", Dy = [
		"mode",
		"battery",
		"grid",
		"power_control",
		"ev_charger",
		"device"
	], Oy = {
		mode: [
			"application_mode",
			"time_of_use_idle_mode",
			"time_of_use_grid_discharge"
		],
		battery: [
			"backup_reserve_soc",
			"battery_charge_soc_limit",
			"battery_discharge_soc_limit_on_grid",
			"battery_discharge_soc_limit_off_grid",
			"battery_charge_power_limit",
			"battery_discharge_power_limit",
			"battery_forced_charge_power_limit"
		],
		grid: [
			"export_limit_mode",
			"export_limit_power",
			"export_limit_current",
			"grid_import_power_limit",
			"grid_export_power_limit"
		],
		ev_charger: [
			"ev_enabled",
			"ev_mode",
			"ev_charge_power"
		],
		device: [
			"buzzer",
			"led_mode",
			"synchronise_clock"
		]
	}, ky = [
		{
			id: "battery",
			signHintKey: "sign_battery"
		},
		{
			id: "grid",
			signHintKey: "sign_grid"
		},
		{
			id: "inverter",
			signHintKey: "sign_inverter"
		}
	], Ay = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [{
			kind: "entity",
			entity: n
		}];
	}), jy = (e) => ky.flatMap((t) => {
		let n = e.get(`${t.id}_power_control`), r = e.get(`${t.id}_power_target`);
		return n === void 0 && r === void 0 ? [] : [{
			kind: "power",
			power: t,
			control: n,
			target: r
		}];
	}), My = ({ entities: e, sections: t }) => Dy.filter((e) => t.includes(e)).map((t) => ({
		id: t,
		rows: t === "power_control" ? jy(e) : Ay({
			entities: e,
			keys: Oy[t]
		})
	})).filter((e) => e.rows.length > 0), Ny = (e) => e.kind === "entity" ? [e.entity] : [e.control, e.target].filter((e) => e !== void 0), Py = class extends Y {
		constructor(...e) {
			super(...e), this.hasControls = !0, this.entityKindKey = "entity_kind_configuration";
		}
		static {
			this.styles = [G, d`
            h3 {
                margin: 12px 0 4px;
                font-size: 0.95rem;
                font-weight: 500;
            }
            .power-row {
                padding: 4px 0;
            }
            .power-name {
                font-weight: 500;
            }
            .power-controls {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px;
            }
            .sign-hint {
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
        `];
		}
		static getConfigForm() {
			return F((e) => [W_({
				name: "sections",
				options: Dy.map((t) => ({
					value: t,
					label: e(`section_${t}`)
				}))
			})]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				sections: [...Dy]
			};
		}
		get cardRows() {
			let { hass: e, config: t } = this;
			return e === void 0 || t?.device === void 0 ? 1 : My({
				entities: k({
					hass: e,
					deviceId: t.device
				}),
				sections: this.sections
			}).reduce((e, t) => e + 1 + t.rows.length, 1);
		}
		shownEntities(e) {
			return My({
				entities: e,
				sections: this.sections
			}).flatMap((e) => e.rows.flatMap(Ny));
		}
		renderBody(e) {
			let t = My({
				entities: e.entities,
				sections: this.sections
			});
			return this.dimmedBody({
				context: e,
				content: x`${this.renderLockedBanner(e)}${t.map((t) => this.renderSection({
					context: e,
					section: t
				}))}`
			});
		}
		get sections() {
			return this.config?.sections ?? Dy;
		}
		renderSection({ context: e, section: t }) {
			return x`<h3>${this.text(`section_${t.id}`)}</h3>
            ${t.rows.map((t) => this.renderRow({
				context: e,
				row: t
			}))}`;
		}
		renderRow({ context: e, row: t }) {
			if (t.kind === "entity") return $({
				context: e,
				entity: t.entity
			});
			let n = (t) => t === void 0 ? w : $({
				context: e,
				entity: t,
				labelHidden: !0
			});
			return x`<div class="power-row">
            <div class="power-name">${this.text(t.power.id)}</div>
            <div class="power-controls">
                ${n(t.control)}${n(t.target)}
            </div>
            ${t.target === void 0 ? w : x`<div class="sign-hint">
                          ${this.text(t.power.signHintKey)}
                      </div>`}
        </div>`;
		}
	}, customElements.define(Ey, Py), R({
		type: Ey,
		nameKey: "controls_card_name",
		descriptionKey: "controls_card_description",
		preview: !0
	});
})), Iy, Ly, Ry, zy, By, Vy, Hy, Uy, Wy, Gy, Ky, qy = t((() => {
	Iy = Date.UTC(2024, 0, 1), Ly = 864e5, Ry = {
		monday: 0,
		tuesday: 1,
		wednesday: 2,
		thursday: 3,
		friday: 4,
		saturday: 5,
		sunday: 6
	}, zy = () => Array.from({ length: 7 }, (e, t) => t), By = (e) => zy().filter((t) => (e >> t) % 2 == 1), Vy = (e) => {
		let t = 0;
		for (let n of new Set(e)) t += 2 ** n;
		return t;
	}, Hy = ({ value: e, day: t }) => {
		let n = new Set(By(e));
		return n.has(t) ? n.delete(t) : n.add(t), Vy(n);
	}, Uy = (e) => {
		let t = new Intl.Locale(e), n = t.getWeekInfo?.() ?? t.weekInfo;
		return n === void 0 ? 0 : n.firstDay - 1;
	}, Wy = ({ language: e, locale: t }) => Ry[t.first_weekday] ?? Uy(e), Gy = (e) => {
		let t = Wy(e);
		return zy().map((e) => (t + e) % 7);
	}, Ky = ({ day: e, language: t, width: n }) => new Intl.DateTimeFormat(t, {
		weekday: n,
		timeZone: "UTC"
	}).format(Iy + e * Ly);
})), Jy, Yy, Xy, Zy, Qy, $y, eb, tb, nb, rb, ib, ab, ob, sb, cb, lb, ub, db, fb = t((() => {
	N(), qy(), Jy = 1440, Yy = ["time_of_use", "time_of_use_bms"], Xy = "application_mode", Zy = 60, Qy = [
		"charge",
		"discharge",
		"ev_charger"
	], $y = {
		charge: "charge",
		discharge: "discharge",
		ev_charger: "ev"
	}, eb = [
		"start",
		"end",
		"days",
		"power"
	], tb = [...eb, "enabled"], nb = [
		...eb,
		"mode",
		"grid_charging",
		"battery_discharge"
	], rb = (e) => e === "ev_charger" ? nb : tb, ib = () => Array.from({ length: 7 }, (e, t) => t + 1), ab = ({ kind: e, number: t }) => `${$y[e]}_slot_${String(t)}`, ob = ({ entities: e, kind: t, number: n }) => {
		let r = ab({
			kind: t,
			number: n
		}), i = rb(t).map((t) => e.get(`${r}_${t}`)), a = i.filter((e) => e !== void 0);
		if (a.length === 0) return {
			slot: null,
			partial: !1
		};
		let o = (t) => e.get(`${r}_${t}`) ?? null, s = o("start"), c = o("end"), l = o("days"), u = o("power");
		return a.length !== i.length || !s || !c || !l || !u ? {
			slot: null,
			partial: !0
		} : {
			slot: {
				kind: t,
				number: n,
				stem: r,
				start: s,
				end: c,
				days: l,
				power: u,
				enabled: o("enabled"),
				mode: o("mode"),
				gridCharging: o("grid_charging"),
				batteryDischarge: o("battery_discharge")
			},
			partial: !1
		};
	}, sb = ({ entities: e, kinds: t }) => {
		let n = [], r = 0;
		for (let i of Qy.filter((e) => t.includes(e))) for (let t of ib()) {
			let a = ob({
				entities: e,
				kind: i,
				number: t
			});
			a.slot !== null && n.push(a.slot), a.partial && (r += 1);
		}
		return {
			slots: n,
			leftOut: r
		};
	}, cb = (e) => e.enabled === null || e.enabled.state.state === "on", lb = (e) => {
		let [t, n] = e.state.state.split(":").map(Number);
		return t === void 0 || n === void 0 || !Number.isFinite(t) || !Number.isFinite(n) ? null : t * Zy + n;
	}, ub = (e) => {
		let t = [];
		for (let n of e) {
			let e = lb(n.start), r = lb(n.end), i = j(n.days);
			if (e === null || r === null || i === null) continue;
			let a = !cb(n), o = (e) => {
				t.push({
					...e,
					slot: n,
					disabled: a
				});
			};
			for (let t = 0; t < 7; t += 1) if ((i >> t) % 2 == 1 && e !== r) {
				if (r > e) {
					o({
						day: t,
						startMinute: e,
						endMinute: r,
						continuation: !1
					});
					continue;
				}
				o({
					day: t,
					startMinute: e,
					endMinute: Jy,
					continuation: !1
				}), o({
					day: (t + 1) % 7,
					startMinute: 0,
					endMinute: r,
					continuation: !0
				});
			}
		}
		return t;
	}, db = ({ entities: e, slots: t }) => {
		let n = e.get(Xy);
		return t.some((e) => e.kind !== "ev_charger") && n !== void 0 && !Yy.includes(n.state.state);
	};
})), pb, mb = t((() => {
	D(), q(), qy(), Q(), pb = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				value: { type: Number },
				draft: { state: !0 }
			};
		}
		static {
			this.styles = [...uv, d`
            :host {
                display: block;
            }
            .input {
                flex: 1;
                min-width: 0;
            }
            .days {
                display: flex;
                flex: 1;
                min-width: 0;
                container-type: inline-size;
                gap: var(--feature-button-spacing, 4px);
            }
            button {
                flex: 1 1 0;
                min-width: 0;
                height: var(--feature-height, 36px);
                padding: 0 2px;
                overflow: hidden;
                background: var(--secondary-background-color, #e5e5e5);
                border: none;
                border-radius: var(--feature-border-radius, 8px);
                cursor: pointer;
            }
            button[aria-pressed="true"] {
                background: var(--primary-color, #03a9f4);
                color: var(--text-primary-color, #fff);
            }
            .narrow {
                display: none;
            }
            @container (max-width: 280px) {
                .short {
                    display: none;
                }
                .narrow {
                    display: inline;
                }
            }
            button:disabled {
                opacity: 0.5;
                cursor: default;
            }
        `];
		}
		constructor() {
			super(), this.delayedCommit = new F_({
				delayMilliseconds: T_,
				commit: (e) => {
					this.draft = null, this.commit(e);
				}
			}), this.onFocusOut = (e) => {
				e.currentTarget.contains(e.relatedTarget) || this.delayedCommit.flush();
			}, this.value = 0, this.draft = null;
		}
		disconnectedCallback() {
			super.disconnectedCallback(), this.delayedCommit.cancel();
		}
		render() {
			let { hass: e } = this;
			if (e === void 0) return x``;
			let { language: t } = e, n = new Set(By(this.draft ?? this.value)), r = Gy(e);
			return this.renderFrame(x`<div
                class="days"
                role="group"
                aria-label=${this.label}
                @focusout=${this.onFocusOut}
            >
                ${r.map((e) => x`<button
                            type="button"
                            aria-pressed=${String(n.has(e))}
                            aria-label=${Ky({
				day: e,
				language: t,
				width: "long"
			})}
                            ?disabled=${this.inactive}
                            @click=${() => {
				this.press(e);
			}}
                        >
                            <span class="short"
                                >${Ky({
				day: e,
				language: t,
				width: "short"
			})}</span
                            ><span class="narrow"
                                >${Ky({
				day: e,
				language: t,
				width: "narrow"
			})}</span
                            >
                        </button>`)}
            </div>`);
		}
		press(e) {
			this.draft = Hy({
				value: this.draft ?? this.value,
				day: e
			}), this.delayedCommit.push(this.draft);
		}
	}, customElements.define("saj-weekday-buttons", pb);
})), hb = /* @__PURE__ */ n({
	SCHEDULE_CARD_TAG: () => gb,
	SajScheduleCard: () => xb
}), gb, _b, vb, yb, bb, xb, Sb = t((() => {
	D(), at(), z(), q(), N(), fb(), K(), qy(), V(), mb(), wy(), X(), L(), gb = "saj-local-schedule-card", _b = 4, vb = !0, yb = {
		charge: "var(--energy-battery-in-color, #4db6ac)",
		discharge: "var(--energy-battery-out-color, #a280db)",
		ev_charger: "var(--energy-grid-consumption-color, #488fc2)"
	}, bb = (e) => e / Jy * 100, xb = class extends Y {
		static {
			this.properties = {
				...Y.properties,
				expanded: { state: !0 }
			};
		}
		static {
			this.styles = [G, d`
            .timeline {
                display: flex;
                flex-direction: column;
                gap: 4px;
                margin-bottom: 12px;
            }
            .day {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .day-name {
                width: 36px;
                color: var(--secondary-text-color, #727272);
                font-size: 0.8rem;
            }
            .track {
                position: relative;
                flex: 1;
                height: 16px;
                background: var(--divider-color, #e0e0e0);
                border-radius: 4px;
            }
            .bar {
                position: absolute;
                top: 0;
                height: 100%;
                min-width: 4px;
                padding: 0;
                background: var(--bar-colour);
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .bar.disabled {
                background: repeating-linear-gradient(
                    45deg,
                    var(--bar-colour) 0 4px,
                    transparent 4px 8px
                );
            }
            h3 {
                margin: 12px 0 4px;
                font-size: 0.95rem;
                font-weight: 500;
            }
            .slot-header {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .summary {
                display: flex;
                flex: 1;
                align-items: center;
                gap: 8px;
                padding: 6px 0;
                background: none;
                border: none;
                cursor: pointer;
                text-align: start;
            }
            .summary .slot-name {
                font-weight: 500;
            }
            .summary .slot-detail {
                color: var(--secondary-text-color, #727272);
            }
            .summary[aria-expanded="true"] saj-icon {
                transform: rotate(180deg);
            }
            .editor {
                padding: 4px 0 8px 32px;
            }
            .left-out {
                margin-top: 8px;
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
        `];
		}
		static getConfigForm() {
			return F((e) => [W_({
				name: "slot_kinds",
				options: Qy.map((t) => ({
					value: t,
					label: e(`option_kind_${t}`)
				}))
			}), P({
				name: "show_timeline",
				fallback: vb
			})]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				slot_kinds: [...Qy]
			};
		}
		constructor() {
			super(), this.hasControls = !0, this.entityKindKey = "entity_kind_schedule", this.expanded = /* @__PURE__ */ new Set();
		}
		get cardRows() {
			let { hass: e, config: t } = this;
			if (e === void 0 || t?.device === void 0) return 1;
			let { slots: n } = this.scheduleFor(k({
				hass: e,
				deviceId: t.device
			}));
			return 1 + n.length + (this.showTimeline ? _b : 0);
		}
		shownEntities(e) {
			return this.scheduleFor(e).slots.flatMap((e) => this.slotEntities(e));
		}
		emptyMessage(e) {
			let { leftOut: t } = this.scheduleFor(e.entities);
			return t === 0 ? "" : this.text("slots_left_out", { count: t });
		}
		renderBody(e) {
			let { slots: t, leftOut: n } = this.scheduleFor(e.entities);
			return this.dimmedBody({
				context: e,
				content: x`${this.renderLockedBanner(e)}${this.renderNotice(e, t)}${this.showTimeline ? this.renderTimeline(e, t) : w}${Qy.filter((e) => t.some((t) => t.kind === e)).map((n) => this.renderKind({
					context: e,
					kind: n,
					slots: t.filter((e) => e.kind === n)
				}))}${n === 0 ? w : x`<div class="left-out">
                          ${this.text("slots_left_out", { count: n })}
                      </div>`}`
			});
		}
		scheduleFor(e) {
			let { kinds: t } = this;
			return (this.scheduled?.entities !== e || this.scheduled.kinds !== t) && (this.scheduled = {
				entities: e,
				kinds: t,
				schedule: sb({
					entities: e,
					kinds: t
				})
			}), this.scheduled.schedule;
		}
		get kinds() {
			return this.config?.slot_kinds ?? Qy;
		}
		get showTimeline() {
			return this.config?.show_timeline ?? vb;
		}
		slotEntities(e) {
			return [
				e.start,
				e.end,
				e.days,
				e.power,
				e.enabled,
				e.mode,
				e.gridCharging,
				e.batteryDischarge
			].filter((e) => e !== null);
		}
		renderNotice(e, t) {
			let n = e.entities.get(Xy);
			return n === void 0 || !db({
				entities: e.entities,
				slots: t
			}) ? w : x`<saj-notice
            tone="warning"
            .message=${this.text("time_of_use_notice")}
            >${$({
				context: e,
				entity: n,
				labelHidden: !0
			})}</saj-notice
        >`;
		}
		renderTimeline(e, t) {
			let n = ub(t), { language: r } = e.hass;
			return x`<div
            class="timeline"
            role="group"
            aria-label=${this.text("week_timeline")}
        >
            ${Gy(e.hass).map((e) => x`<div class="day">
                        <span class="day-name"
                            >${Ky({
				day: e,
				language: r,
				width: "short"
			})}</span
                        >
                        <div class="track">
                            ${n.filter((t) => t.day === e).map((e) => this.renderBar(e))}
                        </div>
                    </div>`)}
        </div>`;
		}
		renderBar(e) {
			let { slot: t } = e;
			return x`<button
            type="button"
            class=${e.disabled ? "bar disabled" : "bar"}
            style=${rt({
				left: `${String(bb(e.startMinute))}%`,
				width: `${String(bb(e.endMinute - e.startMinute))}%`,
				"--bar-colour": yb[t.kind]
			})}
            aria-label=${this.slotName(t)}
            @click=${() => {
				this.expand(t.stem);
			}}
        ></button>`;
		}
		slotName(e) {
			return `${this.text(`option_kind_${e.kind}`)} ${this.text("slot_number", { number: e.number })}`;
		}
		renderKind({ context: e, kind: t, slots: n }) {
			return x`<h3>${this.text(`option_kind_${t}`)}</h3>
            ${n.map((t) => this.renderSlot({
				context: e,
				slot: t
			}))}`;
		}
		renderSlot({ context: e, slot: t }) {
			let { hass: n } = e, r = this.expanded.has(t.stem), i = j(t.days) ?? 0, a = new Set(By(i)), o = Gy(n).filter((e) => a.has(e)).map((e) => Ky({
				day: e,
				language: n.language,
				width: "short"
			})).join(" ");
			return x`<div class="slot">
            <div class="slot-header">
                <button
                    type="button"
                    class="summary"
                    aria-expanded=${String(r)}
                    @click=${() => {
				this.toggle(t.stem);
			}}
                >
                    <saj-icon name="expand"></saj-icon>
                    <span class="slot-name"
                        >${this.text("slot_number", { number: t.number })}</span
                    >
                    <span class="slot-detail"
                        >${n.formatEntityState(t.start.state)} -
                        ${n.formatEntityState(t.end.state)}</span
                    >
                    <span class="slot-detail">${o}</span>
                    <span class="slot-detail"
                        >${n.formatEntityState(t.power.state)}</span
                    >
                </button>
                ${t.enabled === null ? w : $({
				context: e,
				entity: t.enabled,
				labelHidden: !0
			})}
            </div>
            ${r ? this.renderEditor({
				context: e,
				slot: t
			}) : w}
        </div>`;
		}
		renderEditor({ context: e, slot: t }) {
			let { hass: n, lock: r } = e, i = (t) => t === null ? w : $({
				context: e,
				entity: t
			}), { days: a } = t;
			return x`<div class="editor">
            ${i(t.start)}${i(t.end)}${i(t.power)}
            <saj-weekday-buttons
                .hass=${n}
                .label=${this.text("weekdays")}
                .value=${j(a) ?? 0}
                .disabled=${r.locked || A(a)}
                .busy=${this.tracker.isBusy(a.entityId)}
                .error=${this.tracker.errorOf(a.entityId) ?? ""}
                @saj-commit=${(e) => {
				this.tracker.submit({
					entityId: a.entityId,
					request: D_(e.detail)
				});
			}}
            ></saj-weekday-buttons>
            ${i(t.mode)}${i(t.gridCharging)}${i(t.batteryDischarge)}
        </div>`;
		}
		toggle(e) {
			let t = new Set(this.expanded);
			t.delete(e) || t.add(e), this.expanded = t;
		}
		expand(e) {
			this.expanded = /* @__PURE__ */ new Set([...this.expanded, e]);
		}
	}, customElements.define(gb, xb), R({
		type: gb,
		nameKey: "schedule_card_name",
		descriptionKey: "schedule_card_description",
		preview: !0
	});
})), Cb = /* @__PURE__ */ n({
	SajWeekdaysFeature: () => Ob,
	WEEKDAYS_FEATURE_TAG: () => wb,
	supportsWeekdays: () => Db
}), wb, Tb, Eb, Db, Ob, kb = t((() => {
	D(), z(), q(), N(), Wg(), mb(), wy(), wb = "saj-local-weekdays-feature", Tb = "number.", Eb = "_days", Db = ({ hass: e, context: t }) => {
		let n = t.entity_id ?? "";
		return n.startsWith(Tb) && (ig({
			hass: e,
			entityId: n
		})?.key.endsWith(Eb) ?? !1);
	}, Ob = class extends U {
		constructor(...e) {
			super(...e), this.tracker = new P_(this, () => this.hass);
		}
		static {
			this.properties = {
				...U.properties,
				context: { attribute: !1 },
				config: { attribute: !1 }
			};
		}
		static getStubConfig() {
			return { type: `custom:${wb}` };
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			return e === void 0 || n === void 0 ? void 0 : ig({
				hass: e,
				entityId: n
			})?.deviceId;
		}
		render() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			if (e === void 0 || n === void 0) return x``;
			let r = ig({
				hass: e,
				entityId: n
			});
			if (r === null) return x``;
			let i = k({
				hass: e,
				deviceId: r.deviceId
			}), a = i.get(r.key);
			return a === void 0 ? x`` : x`<div
            @click=${(e) => {
				e.stopPropagation();
			}}
        >
            <saj-weekday-buttons
                .hass=${e}
                .label=${Cy({
				hass: e,
				entity: a
			})}
                .labelHidden=${!0}
                .value=${j(a) ?? 0}
                .disabled=${E_(i).locked || A(a)}
                .busy=${this.tracker.isBusy(n)}
                .error=${this.tracker.errorOf(n) ?? ""}
                @saj-commit=${(e) => {
				this.tracker.submit({
					entityId: n,
					request: D_(e.detail)
				});
			}}
            ></saj-weekday-buttons>
        </div>`;
		}
	}, customElements.define(wb, Ob), cg({
		type: wb,
		nameKey: "weekdays_feature_name",
		isSupported: (e, t) => Db({
			hass: e,
			context: t
		}),
		configurable: !1
	});
}));
//#endregion
//#region src/index.ts
i().then(() => Promise.all([
	Promise.resolve().then(() => (Zg(), Kg)),
	Promise.resolve().then(() => (cv(), G_)),
	Promise.resolve().then(() => (vv(), dv)),
	Promise.resolve().then(() => (Jv(), yv)),
	Promise.resolve().then(() => (oy(), Yv)),
	Promise.resolve().then(() => (Fy(), Ty)),
	Promise.resolve().then(() => (Sb(), hb)),
	Promise.resolve().then(() => (kb(), Cb))
]));
//#endregion
