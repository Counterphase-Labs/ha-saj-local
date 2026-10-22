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
	ft = "Choose a SAJ Local system", pt = "SAJ Local status", mt = "Operating state and active fault count of a SAJ Local system", ht = "Not answering", gt = "Unavailable", _t = "Working", vt = "Press", yt = "Week timeline", bt = "Control is off for this system", xt = "Open settings", St = "Nothing to show yet", Ct = "Enable {kind} entities on the system's device page to show them here.", wt = "Open device page", Tt = "reading", Et = "configuration", Dt = "schedule", Ot = "Solar", kt = "Battery", At = "Grid", jt = "Home", Mt = "Inverter", Nt = "EV charger", Pt = "Backup load", Ft = "Meter B", It = "Charging", Lt = "Discharging", Rt = "Importing", zt = "Exporting", Bt = "Idle", Vt = "No faults", Ht = "Faults", Ut = "Control", Wt = "Pack {number}", Gt = "{count} fault", Kt = "{count} faults", qt = "No active faults", Jt = "Clear fault", Yt = "See the diagnostics download for the register and bit", Xt = "Control allowed", Zt = "Control off", Qt = "This system has no battery", $t = "Mode", en = "Running now", tn = "Charge and discharge slots only run in time-of-use mode", nn = "Slot {number}", rn = "{count} slot has disabled entities", an = "{count} slots have disabled entities", on = "Days of the week", sn = "Positive discharges, negative charges", cn = "Positive exports, negative imports", ln = "Positive puts out, negative takes in", un = "Mode", dn = "Battery", fn = "Grid", pn = "Power control", mn = "EV charger", hn = "Device", gn = "System", _n = "Show solar strings", vn = "Show optional equipment", yn = "Scope", bn = "This system", xn = "Parallel system", Sn = "Show today's energy", Cn = "Show groups without faults", wn = "Show battery packs", Tn = "Sections", En = "Slot kinds", Dn = "Charge", On = "Discharge", kn = "EV charger", An = "Show week timeline", jn = "SAJ Local power flow", Mn = "Live power between solar, battery, grid, home and the optional equipment", Nn = "SAJ Local status", Pn = "Operating state, mode, key readings, today's energy, faults and whether control is allowed", Fn = "SAJ Local faults", In = "Active faults per piece of equipment, with clear fault", Ln = "SAJ Local battery", Rn = "State of charge with reserve and limits, battery readings and one row per pack", zn = "SAJ Local controls", Bn = "The shared controls the system offers", Vn = "SAJ Local schedule", Hn = "Charge, discharge and EV charger slots with a week timeline", Un = "SAJ Local weekdays", Wn = {
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
})), Kn, qn, Jn, Yn, Xn, Zn, Qn, $n, O, er, tr, nr = t((() => {
	Gn(), Kn = /* #__PURE__ */ Object.assign({ "./en.json": Wn }), qn = /^\.\/|\.json$/g, Jn = () => new Map(Object.entries(Kn).map(([e, t]) => [e.replace(qn, "").toLowerCase(), t])), Yn = ({ language: e, available: t }) => {
		let n = e.toLowerCase().replaceAll("_", "-");
		return [n, n.replace(/-.*$/, "")].find((e) => t.has(e)) ?? "en";
	}, Xn = ({ template: e, values: t }) => e.replace(/\{(\w+)\}/g, (e, n) => n in t ? String(t[n]) : e), Zn = ({ language: e, available: t }) => {
		let n = t.get(Yn({
			language: e,
			available: t
		})), r = t.get("en"), i = new Intl.PluralRules(e), a = (e) => n?.[e] ?? r?.[e];
		return (e, t = {}) => {
			let n = t.count, r = typeof n == "number" ? `${e}_${i.select(n)}` : void 0, o = (r === void 0 ? void 0 : a(r)) ?? a(e) ?? e;
			return Xn({
				template: o,
				values: t
			});
		};
	}, Qn = /* @__PURE__ */ new Map(), $n = (e) => {
		let t = Qn.get(e);
		if (t !== void 0) return t;
		let n = Zn({
			language: e,
			available: Jn()
		});
		return Qn.set(e, n), n;
	}, O = () => $n(document.documentElement.lang || "en"), er = [
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
	], tr = ({ from: e, now: t, language: n }) => {
		let r = Math.round((e.getTime() - t.getTime()) / 1e3), i = new Intl.RelativeTimeFormat(n, { numeric: "auto" }), a = er.find((e) => Math.abs(r) >= e.seconds);
		return a === void 0 ? i.format(r, "second") : i.format(Math.round(r / a.seconds), a.name);
	};
})), rr, ir, ar, or, sr, cr, k, lr, A, ur, j, M, N = t((() => {
	rr = "saj_local", ir = "unavailable", ar = "unknown", or = (e) => e.platform === "saj_local" && e.device_id !== null && typeof e.translation_key == "string" && e.translation_key !== "", sr = (e) => {
		let t = new Set(Object.values(e.entities).filter(or).map((e) => e.device_id));
		return Object.values(e.devices).filter((e) => t.has(e.id));
	}, cr = ({ hass: e, deviceId: t }) => Object.values(e.entities).filter((e) => or(e) && e.device_id === t).map((e) => e.entity_id), k = ({ hass: e, deviceId: t }) => {
		let n = /* @__PURE__ */ new Map();
		for (let r of Object.values(e.entities)) {
			let i = e.states[r.entity_id];
			or(r) && r.device_id === t && i !== void 0 && n.set(r.translation_key, {
				key: r.translation_key,
				entityId: r.entity_id,
				domain: r.entity_id.replace(/\..*$/, ""),
				state: i
			});
		}
		return n;
	}, lr = ({ hass: e, entityId: t }) => {
		let n = e.entities[t];
		return n === void 0 || !or(n) ? null : {
			deviceId: n.device_id,
			key: n.translation_key
		};
	}, A = (e) => e.state.state === ir, ur = (e) => e.length > 0 && e.every(A), j = (e) => {
		let { state: t } = e.state;
		if (t === ir || t === ar || t === "") return null;
		let n = Number(t);
		return Number.isFinite(n) ? n : null;
	}, M = (e) => e?.state.state === "on";
})), P, dr, fr, F, I, L = t((() => {
	nr(), N(), P = ({ name: e, fallback: t }) => ({
		name: e,
		default: t,
		selector: { boolean: {} }
	}), dr = ({ name: e, options: t, fallback: n }) => ({
		name: e,
		default: n,
		selector: { select: {
			options: t,
			mode: "dropdown"
		} }
	}), fr = {
		name: "device",
		required: !0,
		selector: { device: { filter: { integration: rr } } }
	}, F = (e) => {
		let t = O();
		return {
			schema: [fr, ...e(t)],
			computeLabel: (e) => t(`option_${e.name}`)
		};
	}, I = (e) => {
		let [t] = sr(e);
		return t === void 0 ? {} : { device: t.id };
	};
})), R, pr, mr, z = t((() => {
	nr(), R = ({ type: e, nameKey: t, descriptionKey: n, preview: r }) => {
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
	}, pr = ({ type: e, nameKey: t, isSupported: n, configurable: r }) => {
		window.customCardFeatures ??= [], window.customCardFeatures.push({
			type: e,
			isSupported: n,
			configurable: r,
			get name() {
				return O()(t);
			}
		});
	}, mr = ({ type: e, nameKey: t, descriptionKey: n }) => {
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
})), B, hr, gr, _r, vr, yr, br = t((() => {
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
	], hr = /^battery_pack\d+_(fault|warning)$/, gr = "_fault_unrecognised", _r = ({ definition: e, key: t }) => t.startsWith(`${e.prefix}_fault_`) || e.id === "battery" && hr.test(t), vr = (e) => B.flatMap((t) => {
		let n = e.get(t.summaryKey);
		if (n === void 0) return [];
		let r = [...e.values()].filter((e) => e.domain === "binary_sensor" && M(e) && _r({
			definition: t,
			key: e.key
		})).sort((e, t) => e.key.localeCompare(t.key)).map((e) => ({
			entity: e,
			since: new Date(e.state.last_changed),
			unrecognised: e.key.endsWith(gr)
		}));
		return [{
			id: t.id,
			summary: n,
			active: M(n),
			rows: r
		}];
	}), yr = (e) => B.flatMap((t) => {
		let n = e.get(t.summaryKey);
		return n !== void 0 && M(n) ? [n] : [];
	});
})), xr, Sr, Cr = t((() => {
	xr = new Map(Object.entries({
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
	})), Sr = (e) => xr.get(e ?? "") ?? "disabled";
})), wr, Tr, Er, Dr, Or, kr, Ar, jr, Mr, Nr, Pr, Fr, Ir, Lr, Rr, zr, Br, Vr, Hr = t((() => {
	wr = "M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", Tr = "M16.67,4H15V2H9V4H7.33A1.33,1.33 0 0,0 6,5.33V20.67C6,21.4 6.6,22 7.33,22H16.67A1.33,1.33 0 0,0 18,20.67V5.33C18,4.6 17.4,4 16.67,4Z", Er = "M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z", Dr = "M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z", Or = "M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z", kr = "M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z", Ar = "M12.43 11C12.28 10.84 10 7 7 7S2.32 10.18 2 11V13H11.57C11.72 13.16 14 17 17 17S21.68 13.82 22 13V11H12.43M7 9C8.17 9 9.18 9.85 10 11H4.31C4.78 10.17 5.54 9 7 9M17 15C15.83 15 14.82 14.15 14 13H19.69C19.22 13.83 18.46 15 17 15Z", jr = "M19.77,7.23L19.78,7.22L16.06,3.5L15,4.56L17.11,6.67C16.17,7.03 15.5,7.93 15.5,9A2.5,2.5 0 0,0 18,11.5C18.36,11.5 18.69,11.42 19,11.29V18.5A1,1 0 0,1 18,19.5A1,1 0 0,1 17,18.5V14A2,2 0 0,0 15,12H14V5A2,2 0 0,0 12,3H6A2,2 0 0,0 4,5V21H14V13.5H15.5V18.5A2.5,2.5 0 0,0 18,21A2.5,2.5 0 0,0 20.5,18.5V9C20.5,8.31 20.22,7.68 19.77,7.23M18,10A1,1 0 0,1 17,9A1,1 0 0,1 18,8A1,1 0 0,1 19,9A1,1 0 0,1 18,10M8,18V13.5H6L10,6V11H12L8,18Z", Mr = "M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z", Nr = "M12 20L5 20V12H2L12 3L14.78 5.5H14V7.17C12.84 7.58 12 8.7 12 10V20M15 9H16V7.5H20V9H21C21.55 9 22 9.45 22 10V21C22 21.55 21.55 22 21 22H15C14.45 22 14 21.55 14 21V10C14 9.45 14.45 9 15 9M16 11V14H20V11H16Z", Pr = "M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", Fr = "M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z", Ir = "M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z", Lr = "M12 2C7.04 2 3 6.04 3 11C3 14.91 5.5 18.24 9 19.47V22H11V19.94C11.33 20 11.66 20 12 20S12.67 20 13 19.94V22H15V19.47C18.5 18.23 21 14.9 21 11C21 6.04 16.96 2 12 2M14.25 14L11.25 17L9.75 15.5L11 14.25L9.75 13L12.75 10L14.25 11.5L13 12.75L14.25 14M16 9H8V7H16V9Z", Rr = "M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13", zr = "M11.45,2V5.55L15,3.77L11.45,2M10.45,8L8,10.46L11.75,11.71L10.45,8M2,11.45L3.77,15L5.55,11.45H2M10,2H2V10C2.57,10.17 3.17,10.25 3.77,10.25C7.35,10.26 10.26,7.35 10.27,3.75C10.26,3.16 10.17,2.57 10,2M17,22V16H14L19,7V13H22L17,22Z", Br = "M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z", Vr = "M8.28,5.45L6.5,4.55L7.76,2H16.23L17.5,4.55L15.72,5.44L15,4H9L8.28,5.45M18.62,8H14.09L13.3,5H10.7L9.91,8H5.38L4.1,10.55L5.89,11.44L6.62,10H17.38L18.1,11.45L19.89,10.56L18.62,8M17.77,22H15.7L15.46,21.1L12,15.9L8.53,21.1L8.3,22H6.23L9.12,11H11.19L10.83,12.35L12,14.1L13.16,12.35L12.81,11H14.88L17.77,22M11.4,15L10.5,13.65L9.32,18.13L11.4,15M14.68,18.12L13.5,13.64L12.6,15L14.68,18.12Z";
})), Ur, Wr = t((() => {
	Hr(), Ur = {
		solar: zr,
		battery: Tr,
		grid: Vr,
		home: Mr,
		inverter: Ar,
		ev: jr,
		backup: Nr,
		meter: Lr,
		fault: wr,
		ok: Er,
		lock: Ir,
		settings: kr,
		temperature: Br,
		clock: Or,
		power: Rr,
		info: Pr,
		busy: Fr,
		expand: Dr
	};
})), Gr, V = t((() => {
	D(), Wr(), Gr = class extends E {
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
			return S`<svg viewBox="0 0 24 24" aria-hidden="true"><path d=${Ur[this.name]}></path></svg>`;
		}
	}, customElements.define("saj-icon", Gr);
})), Kr, qr = t((() => {
	N(), Kr = class {
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
			return (this.registry !== e.entities || this.cachedDeviceId !== t) && (this.registry = e.entities, this.cachedDeviceId = t, this.entityIds = t === void 0 ? [] : cr({
				hass: e,
				deviceId: t
			})), this.entityIds;
		}
	};
})), H, Jr = t((() => {
	D(), nr(), H = class extends E {
		static {
			this.properties = { hass: { attribute: !1 } };
		}
		get text() {
			return $n(this.hass?.language ?? "en");
		}
	};
})), U, Yr = t((() => {
	qr(), Jr(), U = class extends H {
		constructor(...e) {
			super(...e), this.redraw = new Kr();
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
})), Xr, W, G, K = t((() => {
	D(), Xr = {
		primary: "var(--primary-color, #03a9f4)",
		secondary: "var(--secondary-text-color, #727272)",
		disabled: "var(--disabled-text-color, #bdbdbd)",
		warning: "var(--warning-color, #ff9800)",
		error: "var(--error-color, #db4437)",
		success: "var(--success-color, #43a047)"
	}, W = (e) => e === void 0 ? "inherit" : Xr[e], G = d`
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
})), Zr = /* @__PURE__ */ n({ SajStatusBadge: () => ti }), Qr, $r, ei, ti, ni = t((() => {
	D(), at(), dt(), L(), z(), N(), br(), Cr(), V(), Yr(), K(), Qr = "saj-local-status-badge", $r = `custom:${Qr}`, ei = "operating_mode", ti = class extends U {
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
				type: $r,
				device: sr(e)[0]?.id
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
			let i = r.get(ei), a = [i, ...B.map((e) => r.get(e.summaryKey))].filter((e) => e !== void 0), o = !ur(a), s = yr(r).length, c = o ? i === void 0 ? "" : e.formatEntityState(i.state) : n("not_answering"), l = x`<saj-icon name="inverter"></saj-icon>
            <span
                class="state"
                style=${rt({ color: W(Sr(i?.state.state)) })}
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
	}, customElements.define(Qr, ti), mr({
		type: Qr,
		nameKey: "badge_name",
		descriptionKey: "badge_description"
	});
})), ri, ii, ai, oi, si, ci, li, ui, di, fi = t((() => {
	N(), ri = .8, ii = 1e4, ai = {
		state: "idle",
		line: "none"
	}, oi = {
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
	}, si = ({ kind: e, watts: t }) => {
		if (Math.abs(t) <= 10) return ai;
		let n = oi[e];
		return t > 0 ? n.positive : n.negative;
	}, ci = (e) => {
		let t = Math.log10(10), n = Math.log10(ii), r = (Math.log10(Math.max(Math.abs(e), 10)) - t) / (n - t);
		return Math.max(ri, 6 - 5.2 * Math.min(r, 1));
	}, li = /* @__PURE__ */ new Map([
		["W", 1],
		["kW", 1e3],
		["MW", 1e6]
	]), ui = (e) => {
		let t = j(e);
		if (t === null) return null;
		let n = e.state.attributes.unit_of_measurement;
		return t * ((typeof n == "string" ? li.get(n) : 1) ?? 1);
	}, di = {
		charging: "charging",
		discharging: "discharging",
		importing: "importing",
		exporting: "exporting",
		idle: "idle"
	};
})), pi, mi, hi, gi, _i, vi, yi, bi = t((() => {
	D(), K(), pi = 360, mi = -90, hi = 100, gi = (e) => Math.min(Math.max(e, 0), hi), _i = (e) => {
		let t = (mi + gi(e) / hi * pi) * Math.PI / (pi / 2), n = (e) => ({
			x: 50 + e * Math.cos(t),
			y: 50 + e * Math.sin(t)
		}), r = n(35), i = n(49);
		return {
			x1: r.x,
			y1: r.y,
			x2: i.x,
			y2: i.y
		};
	}, vi = (e) => 2 * Math.PI * 42 * gi(e) / hi, yi = class extends E {
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
                stroke-dasharray="${vi(this.percent)} ${e}"
                transform="rotate(-90 ${50} ${50})"
            ></circle>
            ${this.markers.map((e) => {
				let t = _i(e.percent);
				return S`<line class="marker" x1=${t.x1} y1=${t.y1} x2=${t.x2} y2=${t.y2}><title>${e.label}</title></line>`;
			})}
            <text class="centre-value" x=${50} y=${52} text-anchor="middle">${this.displayValue}</text>
            <text class="centre-caption" x=${50} y=${64} text-anchor="middle">${this.caption}</text>`}
        </svg>`;
		}
	}, customElements.define("saj-ring-gauge", yi);
})), xi, Si = t((() => {
	D(), K(), xi = class extends E {
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
	}, customElements.define("saj-card", xi);
})), Ci, wi = t((() => {
	D(), dt(), V(), Jr(), K(), Ci = class extends H {
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
	}, customElements.define("saj-empty-state", Ci);
})), Ti, Ei, Di = t((() => {
	D(), V(), K(), Ti = {
		primary: "info",
		warning: "info",
		error: "fault"
	}, Ei = class extends E {
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
                .name=${Ti[this.tone]}
                style="color: ${W(this.tone)}"
            ></saj-icon>
            <span class="message">${this.message}</span>
            <slot></slot>
        </div>`;
		}
	}, customElements.define("saj-notice", Ei);
})), Oi, ki = t((() => {
	D(), at(), dt(), V(), K(), Oi = class extends E {
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
	}, customElements.define("saj-value-row", Oi);
})), Ai, ji, Mi, Ni, Pi, Fi, Ii, Li, Ri, zi, Bi, q = t((() => {
	N(), Ai = 1500, ji = (e) => {
		let t = e.get("control_allowed") ?? null;
		return {
			locked: t?.state.state === "off",
			entity: t
		};
	}, Mi = (e) => ({
		domain: "number",
		service: "set_value",
		data: { value: e }
	}), Ni = (e) => ({
		domain: "select",
		service: "select_option",
		data: { option: e }
	}), Pi = (e) => ({
		domain: "time",
		service: "set_value",
		data: { time: e }
	}), Fi = (e) => ({
		domain: "switch",
		service: e ? "turn_on" : "turn_off"
	}), Ii = () => ({
		domain: "button",
		service: "press"
	}), Li = (e) => `component.${rr}.exceptions.${e}.message`, Ri = async ({ hass: e, error: t }) => {
		let n = t ?? {}, r = n.message ?? String(t);
		if (n.translation_domain !== "saj_local" || n.translation_key === void 0) return r;
		let i = (await e.loadBackendTranslation("exceptions", rr))(Li(n.translation_key), n.translation_placeholders);
		return i === "" ? r : i;
	}, zi = class {
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
					this.errors.set(e, await Ri({
						hass: n,
						error: t
					}));
				} finally {
					this.busyEntities.delete(e), this.host.requestUpdate();
				}
			}
		}
	}, Bi = class {
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
})), Vi, Hi, Ui, Wi, Gi, Ki = t((() => {
	N(), Vi = " ", Hi = " - ", Ui = (e) => [e.name_by_user ?? e.name ?? "", e.model ?? ""].filter((e) => e !== "").join(Vi), Wi = (e) => {
		let t = sr(e).map((e) => ({
			device: e,
			base: Ui(e)
		}));
		return new Map(t.map(({ device: e, base: n }) => {
			let r = t.filter((e) => e.base === n).length > 1, i = e.serial_number ?? "";
			return [e.id, r && i !== "" ? `${n}${Hi}${i}` : n];
		}));
	}, Gi = ({ hass: e, deviceId: t }) => Wi(e).get(t) ?? "";
})), qi, Ji, J, Yi, Y, X = t((() => {
	D(), Si(), wi(), Di(), ki(), Yr(), N(), q(), Ki(), qi = "opacity: 0.5", Ji = [{ type: "entity" }], J = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [n];
	}), Yi = ({ name: e, options: t }) => ({
		name: e,
		default: t.map((e) => e.value),
		selector: { select: {
			options: t,
			multiple: !0,
			mode: "list"
		} }
	}), Y = class extends U {
		constructor(...e) {
			super(...e), this.hasControls = !1, this.entityKindKey = "entity_kind_reading", this.tracker = new zi(this, () => this.hass);
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
			return e.hass.formatEntityName(t.state, Ji);
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
			return x`<div style=${e.dimmed ? qi : ""}>
            ${t}
        </div>`;
		}
		render() {
			let { hass: e, config: t } = this;
			if (e === void 0 || t === void 0) return w;
			let { device: n } = t, r = n === void 0 ? /* @__PURE__ */ new Map() : k({
				hass: e,
				deviceId: n
			}), i = n === void 0 ? "" : Gi({
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
				lock: ji(n),
				tracker: this.tracker,
				dimmed: ur(r)
			};
			return r.length === 0 ? this.renderEmpty(i) : x`${i.dimmed ? x`<saj-notice
                      tone="warning"
                      .message=${this.text("not_answering")}
                  ></saj-notice>` : w}${this.renderBody(i)}`;
		}
	};
})), Xi = /* @__PURE__ */ n({
	BATTERY_CARD_TYPE: () => Zi,
	SajLocalBatteryCard: () => ua
}), Zi, Qi, $i, ea, ta, na, ra, ia, aa, oa, sa, ca, la, ua, da = t((() => {
	D(), dt(), z(), N(), fi(), bi(), K(), L(), X(), Zi = "saj-local-battery-card", Qi = 5, $i = !0, ea = "battery_soc", ta = "battery_power", na = " · ", ra = [
		"backup_reserve_soc",
		"battery_charge_soc_limit",
		"battery_discharge_soc_limit_on_grid"
	], ia = [
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
	], aa = [
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
	], oa = [{
		key: "fault",
		tone: "error"
	}, {
		key: "warning",
		tone: "warning"
	}], sa = /^battery_pack(\d+)_/, ca = 10, la = ({ number: e, field: t }) => `battery_pack${String(e)}_${t}`, ua = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = Qi;
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
				fallback: $i
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		get showPacks() {
			return this.config?.show_packs ?? $i;
		}
		packNumbers(e) {
			let t = /* @__PURE__ */ new Set();
			for (let n of e.keys()) {
				let e = sa.exec(n);
				e?.[1] !== void 0 && t.add(Number.parseInt(e[1], ca));
			}
			return [...t].sort((e, t) => e - t);
		}
		packEntities({ entities: e, number: t }) {
			return J({
				entities: e,
				keys: [...aa, ...oa].map(({ key: e }) => la({
					number: t,
					field: e
				}))
			});
		}
		shownEntities(e) {
			if (!e.has(ea)) return [];
			let t = [
				ea,
				...ra,
				ta,
				...ia.map(({ key: e }) => e)
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
				keys: [ea]
			}).map((t) => this.renderGauge({
				context: e,
				soc: t
			}))}
        ${J({
				entities: t,
				keys: [ta]
			}).map((t) => this.renderPower({
				context: e,
				power: t
			}))}
        ${ia.map(({ key: n, icon: r }) => J({
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
			let n = ra.flatMap((t) => {
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
			let n = ui(t), r = n === null ? void 0 : di[si({
				kind: "battery",
				watts: n
			}).state], i = [this.valueText({
				context: e,
				entity: t,
				absolute: !0
			}), ...r === void 0 ? [] : [this.text(r)]].join(na);
			return this.valueRow({
				context: e,
				entity: t,
				icon: "battery",
				value: i
			});
		}
		renderPack({ context: e, number: t }) {
			let { entities: n } = e;
			return x`<h3>
                ${this.text("battery_pack", { number: t })}${oa.map(({ key: r, tone: i }) => {
				let a = n.get(la({
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
            ${aa.map(({ key: r, icon: i }) => {
				let a = n.get(la({
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
	}, customElements.define(Zi, ua), R({
		type: Zi,
		nameKey: "battery_card_name",
		descriptionKey: "battery_card_description",
		preview: !0
	});
})), fa, pa, Z, Q = t((() => {
	D(), V(), Jr(), K(), fa = "saj-commit", pa = [G, d`
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
			this.styles = pa;
		}
		constructor() {
			super(), this.label = "", this.labelHidden = !1, this.disabled = !1, this.busy = !1, this.error = "";
		}
		get inactive() {
			return this.disabled || this.busy;
		}
		commit(e) {
			this.dispatchEvent(new CustomEvent(fa, {
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
})), ma = /* @__PURE__ */ n({
	FAULTS_CARD_TYPE: () => ha,
	SajLocalFaultsCard: () => ba
}), ha, ga, _a, va, ya, ba, xa = t((() => {
	D(), nr(), z(), q(), br(), Q(), L(), X(), ha = "saj-local-faults-card", ga = 4, _a = !0, va = "clear_current_fault", ya = {
		inverter: "inverter",
		battery: "battery",
		ev: "ev_charger"
	}, ba = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = ga, this.hasControls = !0;
		}
		static {
			this.styles = [...pa, d`
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
				fallback: _a
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		shownEntities(e) {
			return vr(e).map(({ summary: e }) => e);
		}
		renderBody(e) {
			let t = this.config?.show_groups_without_faults ?? _a, n = vr(e.entities).filter(({ active: e }) => e || t), r = e.entities.has(va);
			return x`${r ? this.renderLockedBanner(e) : w}${n.map((t) => this.renderGroup({
				context: e,
				group: t
			}))}`;
		}
		renderGroup({ context: e, group: t }) {
			let n = this.text(ya[t.id]);
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
			let n = tr({
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
			let t = e.entities.get(va);
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
					request: Ii()
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
	}, customElements.define(ha, ba), R({
		type: ha,
		nameKey: "faults_card_name",
		descriptionKey: "faults_card_description",
		preview: !0
	});
})), Sa = /* @__PURE__ */ n({
	POWER_FLOW_CARD_TYPE: () => Ca,
	POWER_FLOW_SCOPES: () => Oa,
	SajLocalPowerFlowCard: () => Xa,
	VIEW_HEIGHT: () => 520,
	VIEW_WIDTH: () => 400
}), Ca, wa, Ta, Ea, Da, Oa, ka, Aa, ja, Ma, Na, Pa, Fa, Ia, La, Ra, za, Ba, Va, Ha, Ua, Wa, Ga, Ka, qa, Ja, Ya, Xa, Za = t((() => {
	D(), dt(), z(), Cr(), fi(), Wr(), K(), L(), X(), Ca = "saj-local-power-flow-card", wa = 6, Ta = !1, Ea = !0, Da = "system", Oa = ["system", "parallel"], ka = 104, Aa = 84, ja = 12, Ma = 24, Na = -38, Pa = 8, Fa = 22, Ia = 35, La = 16, Ra = 16, za = " · ", Ba = 460, Va = {
		x: 200,
		y: 225
	}, Ha = {
		x: 200,
		y: 50
	}, Ua = [
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
			position: Ha
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
	], Wa = "operating_mode", Ga = /^pv([1-9]\d*)_power$/, Ka = /\D/g, qa = {
		idle: "var(--divider-color, #e0e0e0)",
		producing: "var(--energy-solar-color, #ff9800)",
		consuming: "var(--primary-color, #03a9f4)",
		charging: "var(--energy-battery-in-color, #f06292)",
		discharging: "var(--energy-battery-out-color, #4db6ac)",
		importing: "var(--energy-grid-consumption-color, #488fc2)",
		exporting: "var(--energy-grid-return-color, #8353d1)"
	}, Ja = {
		state: "idle",
		line: "none"
	}, Ya = (e) => e.key === "Enter" || e.key === " ", Xa = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = wa;
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
					fallback: Ta
				}),
				P({
					name: "show_optional_equipment",
					fallback: Ea
				}),
				dr({
					name: "scope",
					options: Oa.map((t) => ({
						value: t,
						label: e(`option_scope_${t}`)
					})),
					fallback: Da
				})
			]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				scope: Da
			};
		}
		get scope() {
			return this.config?.scope ?? Da;
		}
		drawnNodes(e) {
			let { scope: t } = this, n = this.config?.show_optional_equipment ?? Ea, r = Ua.flatMap((r) => {
				let i = e.get(r.keys[t]);
				return i === void 0 || r.optional && !n ? [] : [{
					spec: r,
					entity: i
				}];
			}), i = r.filter(({ spec: e }) => e.optional).length, a = 0;
			return r.map(({ spec: n, entity: r }) => {
				let o = ui(r), s = n.secondaryKeys?.[t], c = n.position ?? this.optionalPosition({
					index: a++,
					count: i
				});
				return {
					spec: n,
					entity: r,
					secondaryEntity: s === void 0 ? void 0 : e.get(s),
					watts: o,
					position: c,
					flow: n.kind === null || o === null ? Ja : si({
						kind: n.kind,
						watts: o
					})
				};
			});
		}
		optionalPosition({ index: e, count: t }) {
			return {
				x: 400 * (e + 1) / (t + 1),
				y: Ba
			};
		}
		stringEntities(e) {
			return this.config?.show_strings ?? Ta ? [...e.values()].filter((e) => Ga.test(e.key)).sort((e, t) => this.stringNumber(e) - this.stringNumber(t)) : [];
		}
		stringNumber(e) {
			return Number(e.key.replace(Ka, ""));
		}
		hasScopedReadings(e) {
			let { scope: t } = this;
			return Ua.some(({ keys: n }) => n.system !== n.parallel && e.has(n[t]));
		}
		shownEntities(e) {
			if (this.scope === "parallel" && !this.hasScopedReadings(e)) return [];
			let t = e.get(Wa);
			return [
				...t === void 0 ? [] : [t],
				...this.drawnNodes(e).map(({ entity: e }) => e),
				...this.stringEntities(e)
			];
		}
		renderBody(e) {
			let t = this.drawnNodes(e.entities), n = e.entities.get(Wa), r = this.stringEntities(e.entities);
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
            x2=${Va.x}
            y2=${Va.y}
            style=${i ? `--flow-duration: ${String(ci(r))}s; stroke: ${qa[t.state]}` : ""}
        ></line>`;
		}
		renderNode({ node: e, context: t }) {
			let { spec: n, entity: r, flow: i, position: a } = e, o = n.flowWords ? di[i.state] : void 0, s = [...e.secondaryEntity === void 0 ? [] : [this.valueText({
				context: t,
				entity: e.secondaryEntity
			})], ...o === void 0 || e.watts === null ? [] : [this.text(o)]].join(za);
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
				position: Va,
				icon: "inverter",
				label: this.text("inverter"),
				value: this.valueText({
					context: t,
					entity: e
				}),
				secondary: "",
				colour: W(Sr(e.state.state))
			});
		}
		renderTarget({ entity: e, position: t, icon: n, label: r, value: i, secondary: a, colour: o }) {
			let { x: s, y: c } = t;
			return this.renderTap({
				entity: e,
				label: `${r} ${i} ${a}`.trim(),
				content: S`<rect
                class="box"
                x=${s - ka / 2}
                y=${c - Aa / 2}
                width=${ka}
                height=${Aa}
                rx=${ja}
            ></rect>
            <path
                class="icon"
                d=${Ur[n]}
                transform="translate(${s - Ma / 2} ${c + Na})"
            ></path>
            <text
                class="value"
                x=${s}
                y=${c + Pa}
                text-anchor="middle"
                style=${o === void 0 ? "" : `fill: ${o}`}
            >${i}</text>
            <text class="label" x=${s} y=${c + Fa} text-anchor="middle">${r}</text>
            <text class="secondary" x=${s} y=${c + Ia} text-anchor="middle">${a}</text>`
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
                x=${Ha.x}
                y=${Ha.y + Aa / 2 + Ra + t * La}
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
				Ya(e) && (e.preventDefault(), r());
			}}
        >${n}</g>`;
		}
	}, customElements.define(Ca, Xa), R({
		type: Ca,
		nameKey: "power_flow_card_name",
		descriptionKey: "power_flow_card_description",
		preview: !0
	});
})), Qa = /* @__PURE__ */ n({
	STATUS_CARD_TYPE: () => $a,
	SajLocalStatusCard: () => co
}), $a, eo, to, no, ro, io, ao, oo, so, co, lo = t((() => {
	D(), z(), N(), br(), Cr(), K(), L(), X(), $a = "saj-local-status-card", eo = 5, to = !0, no = [
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
	], ro = [
		"pv_energy_today",
		"load_energy_today",
		"grid_import_energy_today",
		"grid_export_energy_today",
		"battery_charge_energy_today",
		"battery_discharge_energy_today"
	], io = "operating_mode", ao = "application_mode", oo = "application_mode_active", so = "control_allowed", co = class extends Y {
		constructor(...e) {
			super(...e), this.cardRows = eo;
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
				fallback: to
			})]);
		}
		static getStubConfig(e) {
			return I(e);
		}
		get showEnergy() {
			return this.config?.show_energy ?? to;
		}
		shownEntities(e) {
			return J({
				entities: e,
				keys: [
					io,
					ao,
					oo,
					...no.map(({ key: e }) => e),
					...this.showEnergy ? ro : [],
					...B.map(({ summaryKey: e }) => e),
					so
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
			let t = e.entities.get(io);
			return t === void 0 ? [] : [this.valueRow({
				context: e,
				entity: t,
				icon: "inverter",
				tone: Sr(t.state.state)
			})];
		}
		renderMode(e) {
			let t = e.entities.get(ao);
			if (t === void 0) return [];
			let n = e.entities.get(oo);
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
			return no.flatMap(({ key: t, icon: n }) => {
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
				keys: ro
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
			let t = yr(e.entities), [n] = t, r = t.length;
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
			let t = e.entities.get(so);
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
	}, customElements.define($a, co), R({
		type: $a,
		nameKey: "status_card_name",
		descriptionKey: "status_card_description",
		preview: !0
	});
})), uo, fo = t((() => {
	Ke(), uo = (e) => e ?? w;
})), po = t((() => {
	fo();
})), mo, ho, go = t((() => {
	D(), po(), Q(), mo = ({ mode: e, range: t }) => {
		if (e !== "auto") return e;
		let { min: n, max: r, step: i } = t;
		return n === void 0 || r === void 0 || i === void 0 ? "box" : (r - n) / i <= 256 ? "slider" : "box";
	}, ho = class extends Z {
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
			let e = mo({
				mode: this.mode,
				range: {
					min: this.min,
					max: this.max,
					step: this.step
				}
			}) === "slider";
			return this.renderFrame(x`<input
                    type=${e ? "range" : "number"}
                    min=${uo(this.min)}
                    max=${uo(this.max)}
                    step=${uo(this.step)}
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
	}, customElements.define("saj-number-control", ho);
})), _o, vo = t((() => {
	D(), Q(), _o = class extends Z {
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
	}, customElements.define("saj-press-control", _o);
})), yo, bo = t((() => {
	D(), Q(), yo = class extends Z {
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
	}, customElements.define("saj-select-control", yo);
})), xo, So = t((() => {
	D(), Q(), xo = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				checked: { type: Boolean }
			};
		}
		static {
			this.styles = [...pa, d`
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
	}, customElements.define("saj-switch", xo);
})), Co, wo, To = t((() => {
	D(), Q(), Co = 5, wo = class extends Z {
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
			return this.value.slice(0, Co);
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
	}, customElements.define("saj-time-control", wo);
})), Eo, Do, Oo, ko = t((() => {
	D(), q(), N(), go(), vo(), bo(), So(), To(), ki(), Eo = [{ type: "entity" }], Do = ({ hass: e, entity: t }) => e.formatEntityName(t.state, Eo), Oo = ({ context: e, entity: t, labelHidden: n = !1 }) => {
		let { hass: r, lock: i, tracker: a } = e, { attributes: o } = t.state, s = Do({
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
				d(Mi(e.detail));
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
				d(Ni(e.detail));
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
				d(Fi(e.detail));
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
				d(Pi(e.detail));
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
				d(Ii());
			}}
            ></saj-press-control>`;
			default: return x`<saj-value-row
                .label=${s}
                .value=${r.formatEntityState(t.state)}
                .entityId=${t.entityId}
            ></saj-value-row>`;
		}
	};
})), Ao = /* @__PURE__ */ n({
	CONTROLS_CARD_TAG: () => jo,
	SECTION_IDS: () => Mo,
	SajControlsCard: () => zo
}), jo, Mo, No, Po, Fo, Io, Lo, Ro, zo, Bo = t((() => {
	D(), z(), N(), X(), K(), L(), ko(), jo = "saj-local-controls-card", Mo = [
		"mode",
		"battery",
		"grid",
		"power_control",
		"ev_charger",
		"device"
	], No = {
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
	}, Po = [
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
	], Fo = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [{
			kind: "entity",
			entity: n
		}];
	}), Io = (e) => Po.flatMap((t) => {
		let n = e.get(`${t.id}_power_control`), r = e.get(`${t.id}_power_target`);
		return n === void 0 && r === void 0 ? [] : [{
			kind: "power",
			power: t,
			control: n,
			target: r
		}];
	}), Lo = ({ entities: e, sections: t }) => Mo.filter((e) => t.includes(e)).map((t) => ({
		id: t,
		rows: t === "power_control" ? Io(e) : Fo({
			entities: e,
			keys: No[t]
		})
	})).filter((e) => e.rows.length > 0), Ro = (e) => e.kind === "entity" ? [e.entity] : [e.control, e.target].filter((e) => e !== void 0), zo = class extends Y {
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
			return F((e) => [Yi({
				name: "sections",
				options: Mo.map((t) => ({
					value: t,
					label: e(`section_${t}`)
				}))
			})]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				sections: [...Mo]
			};
		}
		get cardRows() {
			let { hass: e, config: t } = this;
			return e === void 0 || t?.device === void 0 ? 1 : Lo({
				entities: k({
					hass: e,
					deviceId: t.device
				}),
				sections: this.sections
			}).reduce((e, t) => e + 1 + t.rows.length, 1);
		}
		shownEntities(e) {
			return Lo({
				entities: e,
				sections: this.sections
			}).flatMap((e) => e.rows.flatMap(Ro));
		}
		renderBody(e) {
			let t = Lo({
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
			return this.config?.sections ?? Mo;
		}
		renderSection({ context: e, section: t }) {
			return x`<h3>${this.text(`section_${t.id}`)}</h3>
            ${t.rows.map((t) => this.renderRow({
				context: e,
				row: t
			}))}`;
		}
		renderRow({ context: e, row: t }) {
			if (t.kind === "entity") return Oo({
				context: e,
				entity: t.entity
			});
			let n = (t) => t === void 0 ? w : Oo({
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
	}, customElements.define(jo, zo), R({
		type: jo,
		nameKey: "controls_card_name",
		descriptionKey: "controls_card_description",
		preview: !0
	});
})), Vo, Ho, Uo, Wo, Go, Ko, qo, Jo, Yo, Xo, Zo, Qo = t((() => {
	Vo = Date.UTC(2024, 0, 1), Ho = 864e5, Uo = {
		monday: 0,
		tuesday: 1,
		wednesday: 2,
		thursday: 3,
		friday: 4,
		saturday: 5,
		sunday: 6
	}, Wo = () => Array.from({ length: 7 }, (e, t) => t), Go = (e) => Wo().filter((t) => (e >> t) % 2 == 1), Ko = (e) => {
		let t = 0;
		for (let n of new Set(e)) t += 2 ** n;
		return t;
	}, qo = ({ value: e, day: t }) => {
		let n = new Set(Go(e));
		return n.has(t) ? n.delete(t) : n.add(t), Ko(n);
	}, Jo = (e) => {
		let t = new Intl.Locale(e), n = t.getWeekInfo?.() ?? t.weekInfo;
		return n === void 0 ? 0 : n.firstDay - 1;
	}, Yo = ({ language: e, locale: t }) => Uo[t.first_weekday] ?? Jo(e), Xo = (e) => {
		let t = Yo(e);
		return Wo().map((e) => (t + e) % 7);
	}, Zo = ({ day: e, language: t, width: n }) => new Intl.DateTimeFormat(t, {
		weekday: n,
		timeZone: "UTC"
	}).format(Vo + e * Ho);
})), $o, es, ts, ns, $, rs, is, as, os, ss, cs, ls, us, ds, fs, ps, ms, hs, gs = t((() => {
	N(), Qo(), $o = 1440, es = ["time_of_use", "time_of_use_bms"], ts = "application_mode", ns = 60, $ = [
		"charge",
		"discharge",
		"ev_charger"
	], rs = {
		charge: "charge",
		discharge: "discharge",
		ev_charger: "ev"
	}, is = [
		"start",
		"end",
		"days",
		"power"
	], as = [...is, "enabled"], os = [
		...is,
		"mode",
		"grid_charging",
		"battery_discharge"
	], ss = (e) => e === "ev_charger" ? os : as, cs = () => Array.from({ length: 7 }, (e, t) => t + 1), ls = ({ kind: e, number: t }) => `${rs[e]}_slot_${String(t)}`, us = ({ entities: e, kind: t, number: n }) => {
		let r = ls({
			kind: t,
			number: n
		}), i = ss(t).map((t) => e.get(`${r}_${t}`)), a = i.filter((e) => e !== void 0);
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
	}, ds = ({ entities: e, kinds: t }) => {
		let n = [], r = 0;
		for (let i of $.filter((e) => t.includes(e))) for (let t of cs()) {
			let a = us({
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
	}, fs = (e) => e.enabled === null || e.enabled.state.state === "on", ps = (e) => {
		let [t, n] = e.state.state.split(":").map(Number);
		return t === void 0 || n === void 0 || !Number.isFinite(t) || !Number.isFinite(n) ? null : t * ns + n;
	}, ms = (e) => {
		let t = [];
		for (let n of e) {
			let e = ps(n.start), r = ps(n.end), i = j(n.days);
			if (e === null || r === null || i === null) continue;
			let a = !fs(n), o = (e) => {
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
					endMinute: $o,
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
	}, hs = ({ entities: e, slots: t }) => {
		let n = e.get(ts);
		return t.some((e) => e.kind !== "ev_charger") && n !== void 0 && !es.includes(n.state.state);
	};
})), _s, vs = t((() => {
	D(), q(), Qo(), Q(), _s = class extends Z {
		static {
			this.properties = {
				...Z.properties,
				value: { type: Number },
				draft: { state: !0 }
			};
		}
		static {
			this.styles = [...pa, d`
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
			super(), this.delayedCommit = new Bi({
				delayMilliseconds: Ai,
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
			let { language: t } = e, n = new Set(Go(this.draft ?? this.value)), r = Xo(e);
			return this.renderFrame(x`<div
                class="days"
                role="group"
                aria-label=${this.label}
                @focusout=${this.onFocusOut}
            >
                ${r.map((e) => x`<button
                            type="button"
                            aria-pressed=${String(n.has(e))}
                            aria-label=${Zo({
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
                                >${Zo({
				day: e,
				language: t,
				width: "short"
			})}</span
                            ><span class="narrow"
                                >${Zo({
				day: e,
				language: t,
				width: "narrow"
			})}</span
                            >
                        </button>`)}
            </div>`);
		}
		press(e) {
			this.draft = qo({
				value: this.draft ?? this.value,
				day: e
			}), this.delayedCommit.push(this.draft);
		}
	}, customElements.define("saj-weekday-buttons", _s);
})), ys = /* @__PURE__ */ n({
	SCHEDULE_CARD_TAG: () => bs,
	SajScheduleCard: () => Ts
}), bs, xs, Ss, Cs, ws, Ts, Es = t((() => {
	D(), at(), z(), q(), N(), gs(), K(), Qo(), V(), vs(), ko(), X(), L(), bs = "saj-local-schedule-card", xs = 4, Ss = !0, Cs = {
		charge: "var(--energy-battery-in-color, #4db6ac)",
		discharge: "var(--energy-battery-out-color, #a280db)",
		ev_charger: "var(--energy-grid-consumption-color, #488fc2)"
	}, ws = (e) => e / $o * 100, Ts = class extends Y {
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
			return F((e) => [Yi({
				name: "slot_kinds",
				options: $.map((t) => ({
					value: t,
					label: e(`option_kind_${t}`)
				}))
			}), P({
				name: "show_timeline",
				fallback: Ss
			})]);
		}
		static getStubConfig(e) {
			return {
				...I(e),
				slot_kinds: [...$]
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
			return 1 + n.length + (this.showTimeline ? xs : 0);
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
				content: x`${this.renderLockedBanner(e)}${this.renderNotice(e, t)}${this.showTimeline ? this.renderTimeline(e, t) : w}${$.filter((e) => t.some((t) => t.kind === e)).map((n) => this.renderKind({
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
				schedule: ds({
					entities: e,
					kinds: t
				})
			}), this.scheduled.schedule;
		}
		get kinds() {
			return this.config?.slot_kinds ?? $;
		}
		get showTimeline() {
			return this.config?.show_timeline ?? Ss;
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
			let n = e.entities.get(ts);
			return n === void 0 || !hs({
				entities: e.entities,
				slots: t
			}) ? w : x`<saj-notice
            tone="warning"
            .message=${this.text("time_of_use_notice")}
            >${Oo({
				context: e,
				entity: n,
				labelHidden: !0
			})}</saj-notice
        >`;
		}
		renderTimeline(e, t) {
			let n = ms(t), { language: r } = e.hass;
			return x`<div
            class="timeline"
            role="group"
            aria-label=${this.text("week_timeline")}
        >
            ${Xo(e.hass).map((e) => x`<div class="day">
                        <span class="day-name"
                            >${Zo({
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
				left: `${String(ws(e.startMinute))}%`,
				width: `${String(ws(e.endMinute - e.startMinute))}%`,
				"--bar-colour": Cs[t.kind]
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
			let { hass: n } = e, r = this.expanded.has(t.stem), i = j(t.days) ?? 0, a = new Set(Go(i)), o = Xo(n).filter((e) => a.has(e)).map((e) => Zo({
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
                ${t.enabled === null ? w : Oo({
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
			let { hass: n, lock: r } = e, i = (t) => t === null ? w : Oo({
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
					request: Mi(e.detail)
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
	}, customElements.define(bs, Ts), R({
		type: bs,
		nameKey: "schedule_card_name",
		descriptionKey: "schedule_card_description",
		preview: !0
	});
})), Ds = /* @__PURE__ */ n({
	SajWeekdaysFeature: () => Ms,
	WEEKDAYS_FEATURE_TAG: () => Os,
	supportsWeekdays: () => js
}), Os, ks, As, js, Ms, Ns = t((() => {
	D(), z(), q(), N(), Yr(), vs(), ko(), Os = "saj-local-weekdays-feature", ks = "number.", As = "_days", js = ({ hass: e, context: t }) => {
		let n = t.entity_id ?? "";
		return n.startsWith(ks) && (lr({
			hass: e,
			entityId: n
		})?.key.endsWith(As) ?? !1);
	}, Ms = class extends U {
		constructor(...e) {
			super(...e), this.tracker = new zi(this, () => this.hass);
		}
		static {
			this.properties = {
				...U.properties,
				context: { attribute: !1 },
				config: { attribute: !1 }
			};
		}
		static getStubConfig() {
			return { type: `custom:${Os}` };
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			return e === void 0 || n === void 0 ? void 0 : lr({
				hass: e,
				entityId: n
			})?.deviceId;
		}
		render() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			if (e === void 0 || n === void 0) return x``;
			let r = lr({
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
                .label=${Do({
				hass: e,
				entity: a
			})}
                .labelHidden=${!0}
                .value=${j(a) ?? 0}
                .disabled=${ji(i).locked || A(a)}
                .busy=${this.tracker.isBusy(n)}
                .error=${this.tracker.errorOf(n) ?? ""}
                @saj-commit=${(e) => {
				this.tracker.submit({
					entityId: n,
					request: Mi(e.detail)
				});
			}}
            ></saj-weekday-buttons>
        </div>`;
		}
	}, customElements.define(Os, Ms), pr({
		type: Os,
		nameKey: "weekdays_feature_name",
		isSupported: (e, t) => js({
			hass: e,
			context: t
		}),
		configurable: !1
	});
}));
//#endregion
//#region src/index.ts
i().then(() => Promise.all([
	Promise.resolve().then(() => (ni(), Zr)),
	Promise.resolve().then(() => (da(), Xi)),
	Promise.resolve().then(() => (xa(), ma)),
	Promise.resolve().then(() => (Za(), Sa)),
	Promise.resolve().then(() => (lo(), Qa)),
	Promise.resolve().then(() => (Bo(), Ao)),
	Promise.resolve().then(() => (Es(), ys)),
	Promise.resolve().then(() => (Ns(), Ds))
]));
//#endregion
