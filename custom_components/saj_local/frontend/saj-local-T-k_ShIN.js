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
})), tt, nt, O, rt = t((() => {
	Ke(), et(), tt = "important", nt = " !" + tt, O = Qe(class extends $e {
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
})), it = t((() => {
	rt();
})), at, ot, st, ct, lt, ut = t((() => {
	at = "hass-action", ot = "/config/integrations/integration/saj_local", st = (e) => `/config/devices/device/${e}`, ct = ({ host: e, entityId: t }) => {
		e.dispatchEvent(new CustomEvent(at, {
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
	}, lt = ({ host: e, path: t }) => {
		e.dispatchEvent(new CustomEvent(at, {
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
})), dt, ft, pt, mt, ht, gt, _t, vt, yt, bt, xt, St, Ct, wt, Tt, Et, Dt, Ot, kt, At, jt, Mt, Nt, Pt, Ft, It, Lt, Rt, zt, Bt, Vt, Ht, Ut, Wt, Gt, Kt, qt, Jt, Yt, Xt, Zt, Qt, $t, en, tn, nn, rn, an, on, sn, cn, ln, un, dn, fn, pn, mn, hn, gn, _n, vn, yn, bn, xn, Sn, Cn, wn, Tn, En, Dn, On, kn, An, jn, Mn, Nn, Pn, Fn, In, Ln, Rn, zn, Bn, Vn, Hn, Un, Wn, Gn, Kn, qn = t((() => {
	dt = "SAJ-Local-System auswählen", ft = "SAJ-Local-Status", pt = "Betriebszustand und Anzahl der aktiven Fehler eines SAJ-Local-Systems", mt = "Antwortet nicht", ht = "Nicht verfügbar", gt = "In Arbeit", _t = "Drücken", vt = "Wochenzeitleiste", yt = "Die Steuerung ist für dieses System ausgeschaltet", bt = "Einstellungen öffnen", xt = "Noch nichts anzuzeigen", St = "Aktiviere die Entitäten ({kind}) auf der Geräteseite des Systems, um sie hier anzuzeigen.", Ct = "Geräteseite öffnen", wt = "Messwerte", Tt = "Konfiguration", Et = "Zeitplan", Dt = "Solar", Ot = "Batterie", kt = "Netz", At = "Haus", jt = "Wechselrichter", Mt = "Wallbox", Nt = "Notstromlast", Pt = "Zähler B", Ft = "Laden", It = "Entladen", Lt = "Netzbezug", Rt = "Einspeisung", zt = "Inaktiv", Bt = "Keine Fehler", Vt = "Fehler", Ht = "Steuerung", Ut = "Pack {number}", Wt = "{count} Fehler", Gt = "{count} Fehler", Kt = "Keine aktiven Fehler", qt = "Fehler quittieren", Jt = "Register und Bit stehen im Diagnosedownload", Yt = "Steuerung zugelassen", Xt = "Steuerung aus", Zt = "Dieses System hat keine Batterie", Qt = "Modus", $t = "Läuft gerade", en = "Lade- und Entladezeitfenster laufen nur im Modus Zeitsteuerung", tn = "Zeitfenster {number}", nn = "{count} Zeitfenster hat deaktivierte Entitäten", rn = "{count} Zeitfenster haben deaktivierte Entitäten", an = "Wochentage", on = "Positiv entlädt, negativ lädt", sn = "Positiv speist ein, negativ bezieht", cn = "Positiv gibt ab, negativ nimmt auf", ln = "Modus", un = "Batterie", dn = "Netz", fn = "Leistungssteuerung", pn = "Wallbox", mn = "Gerät", hn = "System", gn = "Solar-Strings anzeigen", _n = "Optionale Ausstattung anzeigen", vn = "Umfang", yn = "Dieses System", bn = "Parallelsystem", xn = "Energie von heute anzeigen", Sn = "Gruppen ohne Fehler anzeigen", Cn = "Batteriepacks anzeigen", wn = "Abschnitte", Tn = "Laden", En = "Entladen", Dn = "Wallbox", On = "Wochenzeitleiste anzeigen", kn = "SAJ-Local-Energiefluss", An = "Live-Leistung zwischen Solar, Batterie, Netz, Haus und der optionalen Ausstattung", jn = "SAJ-Local-Status", Mn = "Betriebszustand, Modus, wichtige Messwerte, Energie von heute, Fehler und ob die Steuerung zugelassen ist", Nn = "SAJ-Local-Fehler", Pn = "Aktive Fehler je Ausstattungsteil, mit Fehler quittieren", Fn = "SAJ-Local-Batterie", In = "Ladezustand mit Reserve und Grenzwerten, Batteriewerte und eine Zeile pro Pack", Ln = "SAJ-Local-Steuerung", Rn = "Die gemeinsamen Bedienelemente des Systems", zn = "SAJ-Local-Ladezeitplan", Bn = "Ladezeitfenster mit einer Wochenzeitleiste", Vn = "SAJ-Local-Entladezeitplan", Hn = "Entladezeitfenster mit einer Wochenzeitleiste", Un = "SAJ-Local-Wallbox-Zeitplan", Wn = "Wallbox-Zeitfenster mit einer Wochenzeitleiste", Gn = "SAJ-Local-Wochentage", Kn = {
		choose_system: dt,
		badge_name: ft,
		badge_description: pt,
		not_answering: mt,
		unavailable: ht,
		busy: gt,
		press: _t,
		week_timeline: vt,
		locked_message: yt,
		open_settings: bt,
		empty_title: xt,
		empty_enable: St,
		open_device_page: Ct,
		entity_kind_reading: wt,
		entity_kind_configuration: Tt,
		entity_kind_schedule: Et,
		solar: Dt,
		battery: Ot,
		grid: kt,
		home: At,
		inverter: jt,
		ev_charger: Mt,
		backup_load: Nt,
		meter_b: Pt,
		charging: Ft,
		discharging: It,
		importing: Lt,
		exporting: Rt,
		idle: zt,
		no_faults: Bt,
		faults: Vt,
		changes: Ht,
		battery_pack: Ut,
		faults_count_one: Wt,
		faults_count_other: Gt,
		no_active_faults: Kt,
		clear_fault: qt,
		see_diagnostics: Jt,
		changes_allowed: Yt,
		changes_off: Xt,
		no_battery: Zt,
		mode: Qt,
		mode_running_now: $t,
		time_of_use_notice: en,
		slot_number: tn,
		slots_left_out_one: nn,
		slots_left_out_other: rn,
		weekdays: an,
		sign_battery: on,
		sign_grid: sn,
		sign_inverter: cn,
		section_mode: ln,
		section_battery: un,
		section_grid: dn,
		section_power_control: fn,
		section_ev_charger: pn,
		section_device: mn,
		option_device: hn,
		option_show_strings: gn,
		option_show_optional_equipment: _n,
		option_scope: vn,
		option_scope_system: yn,
		option_scope_parallel: bn,
		option_show_energy: xn,
		option_show_groups_without_faults: Sn,
		option_show_packs: Cn,
		option_sections: wn,
		option_kind_charge: Tn,
		option_kind_discharge: En,
		option_kind_ev_charger: Dn,
		option_show_timeline: On,
		power_flow_card_name: kn,
		power_flow_card_description: An,
		status_card_name: jn,
		status_card_description: Mn,
		faults_card_name: Nn,
		faults_card_description: Pn,
		battery_card_name: Fn,
		battery_card_description: In,
		controls_card_name: Ln,
		controls_card_description: Rn,
		charge_schedule_card_name: zn,
		charge_schedule_card_description: Bn,
		discharge_schedule_card_name: Vn,
		discharge_schedule_card_description: Hn,
		ev_charger_schedule_card_name: Un,
		ev_charger_schedule_card_description: Wn,
		weekdays_feature_name: Gn
	};
})), Jn, Yn, Xn, Zn, Qn, $n, er, tr, nr, rr, ir, ar, or, sr, cr, lr, ur, dr, fr, pr, mr, hr, gr, _r, vr, yr, br, xr, Sr, Cr, wr, Tr, Er, Dr, Or, kr, Ar, jr, Mr, Nr, Pr, Fr, Ir, Lr, Rr, zr, Br, Vr, Hr, Ur, Wr, Gr, Kr, qr, Jr, Yr, Xr, Zr, Qr, $r, ei, ti, ni, ri, ii, ai, oi, si, ci, li, ui, di, fi, pi, mi, hi, gi, _i, vi, yi, bi, xi, Si, Ci, wi, Ti, Ei, Di, Oi, ki = t((() => {
	Jn = "Choose a SAJ Local system", Yn = "SAJ Local status", Xn = "Operating state and active fault count of a SAJ Local system", Zn = "Not answering", Qn = "Unavailable", $n = "Working", er = "Press", tr = "Week timeline", nr = "Control is off for this system", rr = "Open settings", ir = "Nothing to show yet", ar = "Enable {kind} entities on the system's device page to show them here.", or = "Open device page", sr = "reading", cr = "configuration", lr = "schedule", ur = "Solar", dr = "Battery", fr = "Grid", pr = "Home", mr = "Inverter", hr = "EV charger", gr = "Backup load", _r = "Meter B", vr = "Charging", yr = "Discharging", br = "Importing", xr = "Exporting", Sr = "Idle", Cr = "No faults", wr = "Faults", Tr = "Control", Er = "Pack {number}", Dr = "{count} fault", Or = "{count} faults", kr = "No active faults", Ar = "Clear fault", jr = "See the diagnostics download for the register and bit", Mr = "Control allowed", Nr = "Control off", Pr = "This system has no battery", Fr = "Mode", Ir = "Running now", Lr = "Charge and discharge slots only run in time-of-use mode", Rr = "Slot {number}", zr = "{count} slot has disabled entities", Br = "{count} slots have disabled entities", Vr = "Days of the week", Hr = "Positive discharges, negative charges", Ur = "Positive exports, negative imports", Wr = "Positive puts out, negative takes in", Gr = "Mode", Kr = "Battery", qr = "Grid", Jr = "Power control", Yr = "EV charger", Xr = "Device", Zr = "System", Qr = "Show solar strings", $r = "Show optional equipment", ei = "Scope", ti = "This system", ni = "Parallel system", ri = "Show today's energy", ii = "Show groups without faults", ai = "Show battery packs", oi = "Sections", si = "Charge", ci = "Discharge", li = "EV charger", ui = "Show week timeline", di = "SAJ Local power flow", fi = "Live power between solar, battery, grid, home and the optional equipment", pi = "SAJ Local status", mi = "Operating state, mode, key readings, today's energy, faults and whether control is allowed", hi = "SAJ Local faults", gi = "Active faults per piece of equipment, with clear fault", _i = "SAJ Local battery", vi = "State of charge with reserve and limits, battery readings and one row per pack", yi = "SAJ Local controls", bi = "The shared controls the system offers", xi = "SAJ Local charge schedule", Si = "Charge slots with a week timeline", Ci = "SAJ Local discharge schedule", wi = "Discharge slots with a week timeline", Ti = "SAJ Local EV charger schedule", Ei = "EV charger slots with a week timeline", Di = "SAJ Local weekdays", Oi = {
		choose_system: Jn,
		badge_name: Yn,
		badge_description: Xn,
		not_answering: Zn,
		unavailable: Qn,
		busy: $n,
		press: er,
		week_timeline: tr,
		locked_message: nr,
		open_settings: rr,
		empty_title: ir,
		empty_enable: ar,
		open_device_page: or,
		entity_kind_reading: sr,
		entity_kind_configuration: cr,
		entity_kind_schedule: lr,
		solar: ur,
		battery: dr,
		grid: fr,
		home: pr,
		inverter: mr,
		ev_charger: hr,
		backup_load: gr,
		meter_b: _r,
		charging: vr,
		discharging: yr,
		importing: br,
		exporting: xr,
		idle: Sr,
		no_faults: Cr,
		faults: wr,
		changes: Tr,
		battery_pack: Er,
		faults_count_one: Dr,
		faults_count_other: Or,
		no_active_faults: kr,
		clear_fault: Ar,
		see_diagnostics: jr,
		changes_allowed: Mr,
		changes_off: Nr,
		no_battery: Pr,
		mode: Fr,
		mode_running_now: Ir,
		time_of_use_notice: Lr,
		slot_number: Rr,
		slots_left_out_one: zr,
		slots_left_out_other: Br,
		weekdays: Vr,
		sign_battery: Hr,
		sign_grid: Ur,
		sign_inverter: Wr,
		section_mode: Gr,
		section_battery: Kr,
		section_grid: qr,
		section_power_control: Jr,
		section_ev_charger: Yr,
		section_device: Xr,
		option_device: Zr,
		option_show_strings: Qr,
		option_show_optional_equipment: $r,
		option_scope: ei,
		option_scope_system: ti,
		option_scope_parallel: ni,
		option_show_energy: ri,
		option_show_groups_without_faults: ii,
		option_show_packs: ai,
		option_sections: oi,
		option_kind_charge: si,
		option_kind_discharge: ci,
		option_kind_ev_charger: li,
		option_show_timeline: ui,
		power_flow_card_name: di,
		power_flow_card_description: fi,
		status_card_name: pi,
		status_card_description: mi,
		faults_card_name: hi,
		faults_card_description: gi,
		battery_card_name: _i,
		battery_card_description: vi,
		controls_card_name: yi,
		controls_card_description: bi,
		charge_schedule_card_name: xi,
		charge_schedule_card_description: Si,
		discharge_schedule_card_name: Ci,
		discharge_schedule_card_description: wi,
		ev_charger_schedule_card_name: Ti,
		ev_charger_schedule_card_description: Ei,
		weekdays_feature_name: Di
	};
})), Ai, ji, Mi, Ni, Pi, Fi, Ii, Li, Ri, zi, Bi, Vi, Hi, Ui, Wi, Gi, Ki, qi, Ji, Yi, Xi, Zi, Qi, $i, ea, ta, na, ra, ia, aa, oa, sa, ca, la, ua, da, fa, pa, ma, ha, ga, _a, va, ya, ba, xa, Sa, Ca, wa, Ta, Ea, Da, Oa, ka, Aa, ja, Ma, Na, Pa, Fa, Ia, La, Ra, za, Ba, Va, Ha, Ua, Wa, Ga, Ka, qa, Ja, Ya, Xa, Za, Qa, $a, eo, to, no, ro, io, ao, oo, so, co, lo, uo, fo = t((() => {
	Ai = "Elige un sistema SAJ Local", ji = "Estado de SAJ Local", Mi = "Estado de funcionamiento y número de fallos activos de un sistema SAJ Local", Ni = "Sin respuesta", Pi = "No disponible", Fi = "Procesando", Ii = "Pulsar", Li = "Línea de tiempo semanal", Ri = "El control está desactivado para este sistema", zi = "Abrir ajustes", Bi = "Nada que mostrar todavía", Vi = "Habilita las entidades de {kind} en la página del dispositivo del sistema para mostrarlas aquí.", Hi = "Abrir la página del dispositivo", Ui = "lectura", Wi = "configuración", Gi = "programación", Ki = "Solar", qi = "Batería", Ji = "Casa", Yi = "Inversor", Xi = "Cargador de VE", Zi = "Carga de respaldo", Qi = "Contador B", $i = "Cargando", ea = "Descargando", ta = "Importando", na = "Exportando", ra = "Inactivo", ia = "Sin fallos", aa = "Fallos", oa = "Control", sa = "Módulo {number}", ca = "{count} fallo", la = "{count} de fallos", ua = "{count} fallos", da = "Sin fallos activos", fa = "Borrar fallo", pa = "Consulta la descarga de diagnósticos para ver el registro Modbus y el bit", ma = "Control permitido", ha = "Control desactivado", ga = "Este sistema no tiene batería", _a = "Modo", va = "En marcha ahora", ya = "Las franjas de carga y descarga solo funcionan en el modo horario programado", ba = "Franja {number}", xa = "{count} franja tiene entidades deshabilitadas", Sa = "{count} de franjas tienen entidades deshabilitadas", Ca = "{count} franjas tienen entidades deshabilitadas", wa = "Días de la semana", Ta = "Positivo descarga, negativo carga", Ea = "Positivo exporta, negativo importa", Da = "Positivo entrega, negativo absorbe", Oa = "Modo", ka = "Batería", Aa = "Control de potencia", ja = "Cargador de VE", Ma = "Dispositivo", Na = "Sistema", Pa = "Mostrar strings solares", Fa = "Mostrar equipo opcional", Ia = "Ámbito", La = "Este sistema", Ra = "Sistema en paralelo", za = "Mostrar la energía de hoy", Ba = "Mostrar grupos sin fallos", Va = "Mostrar módulos de batería", Ha = "Secciones", Ua = "Carga", Wa = "Descarga", Ga = "Cargador de VE", Ka = "Mostrar línea de tiempo semanal", qa = "Flujo de potencia de SAJ Local", Ja = "Potencia en vivo entre solar, batería, red, casa y el equipo opcional", Ya = "Estado de SAJ Local", Xa = "Estado de funcionamiento, modo, lecturas clave, energía de hoy, fallos y si se permite el control", Za = "Fallos de SAJ Local", Qa = "Fallos activos por equipo, con borrar fallo", $a = "Batería de SAJ Local", eo = "Estado de carga con reserva y límites, lecturas de la batería y una fila por módulo", to = "Controles de SAJ Local", no = "Los controles compartidos que ofrece el sistema", ro = "Programación de carga de SAJ Local", io = "Franjas de carga con una línea de tiempo semanal", ao = "Programación de descarga de SAJ Local", oo = "Franjas de descarga con una línea de tiempo semanal", so = "Programación del cargador de VE de SAJ Local", co = "Franjas del cargador de VE con una línea de tiempo semanal", lo = "Días de la semana de SAJ Local", uo = {
		choose_system: Ai,
		badge_name: ji,
		badge_description: Mi,
		not_answering: Ni,
		unavailable: Pi,
		busy: Fi,
		press: Ii,
		week_timeline: Li,
		locked_message: Ri,
		open_settings: zi,
		empty_title: Bi,
		empty_enable: Vi,
		open_device_page: Hi,
		entity_kind_reading: Ui,
		entity_kind_configuration: Wi,
		entity_kind_schedule: Gi,
		solar: Ki,
		battery: qi,
		grid: "Red",
		home: Ji,
		inverter: Yi,
		ev_charger: Xi,
		backup_load: Zi,
		meter_b: Qi,
		charging: $i,
		discharging: ea,
		importing: ta,
		exporting: na,
		idle: ra,
		no_faults: ia,
		faults: aa,
		changes: oa,
		battery_pack: sa,
		faults_count_one: ca,
		faults_count_many: la,
		faults_count_other: ua,
		no_active_faults: da,
		clear_fault: fa,
		see_diagnostics: pa,
		changes_allowed: ma,
		changes_off: ha,
		no_battery: ga,
		mode: _a,
		mode_running_now: va,
		time_of_use_notice: ya,
		slot_number: ba,
		slots_left_out_one: xa,
		slots_left_out_many: Sa,
		slots_left_out_other: Ca,
		weekdays: wa,
		sign_battery: Ta,
		sign_grid: Ea,
		sign_inverter: Da,
		section_mode: Oa,
		section_battery: ka,
		section_grid: "Red",
		section_power_control: Aa,
		section_ev_charger: ja,
		section_device: Ma,
		option_device: Na,
		option_show_strings: Pa,
		option_show_optional_equipment: Fa,
		option_scope: Ia,
		option_scope_system: La,
		option_scope_parallel: Ra,
		option_show_energy: za,
		option_show_groups_without_faults: Ba,
		option_show_packs: Va,
		option_sections: Ha,
		option_kind_charge: Ua,
		option_kind_discharge: Wa,
		option_kind_ev_charger: Ga,
		option_show_timeline: Ka,
		power_flow_card_name: qa,
		power_flow_card_description: Ja,
		status_card_name: Ya,
		status_card_description: Xa,
		faults_card_name: Za,
		faults_card_description: Qa,
		battery_card_name: $a,
		battery_card_description: eo,
		controls_card_name: to,
		controls_card_description: no,
		charge_schedule_card_name: ro,
		charge_schedule_card_description: io,
		discharge_schedule_card_name: ao,
		discharge_schedule_card_description: oo,
		ev_charger_schedule_card_name: so,
		ev_charger_schedule_card_description: co,
		weekdays_feature_name: lo
	};
})), po, mo, ho, go, _o, vo, yo, bo, xo, So, Co, wo, To, Eo, Do, Oo, ko, Ao, jo, Mo, No, Po, Fo, Io, Lo, Ro, zo, Bo, Vo, Ho, Uo, Wo, Go, Ko, qo, Jo, Yo, Xo, Zo, Qo, $o, es, ts, ns, rs, is, as, os, ss, cs, ls, us, ds, fs, ps, ms, hs, gs, _s, vs, ys, bs, xs, Ss, Cs, ws, Ts, Es, Ds, Os, ks, As, js, Ms, Ns, Ps, Fs, Is, Ls, Rs, zs, Bs, Vs, Hs, Us, Ws, Gs, Ks, qs, Js, Ys, Xs = t((() => {
	po = "Choisir un système SAJ Local", mo = "État de SAJ Local", ho = "État de fonctionnement et nombre de défauts actifs d'un système SAJ Local", go = "Ne répond pas", _o = "Indisponible", vo = "En cours", yo = "Appuyer", bo = "Chronologie de la semaine", xo = "Le contrôle est désactivé pour ce système", So = "Ouvrir les paramètres", Co = "Rien à afficher pour le moment", wo = "Activez les entités de {kind} sur la page de l'appareil du système pour les afficher ici.", To = "Ouvrir la page de l'appareil", Eo = "mesure", Do = "configuration", Oo = "programme", ko = "Solaire", Ao = "Batterie", jo = "Réseau", Mo = "Maison", No = "Onduleur", Po = "Chargeur de VE", Fo = "Circuit de secours", Io = "Compteur B", Lo = "Charge", Ro = "Décharge", zo = "Soutirage", Bo = "Injection", Vo = "Inactif", Ho = "Aucun défaut", Uo = "Défauts", Wo = "Contrôle", Go = "Module {number}", Ko = "{count} défaut", qo = "{count} de défauts", Jo = "{count} défauts", Yo = "Aucun défaut actif", Xo = "Effacer le défaut", Zo = "Consultez le téléchargement des diagnostics pour le registre et le bit", Qo = "Contrôle autorisé", $o = "Contrôle désactivé", es = "Ce système n'a pas de batterie", ts = "Mode", ns = "En cours", rs = "Les plages de charge et de décharge ne s'exécutent qu'en mode horaire", is = "Plage {number}", as = "{count} plage a des entités désactivées", os = "{count} de plages ont des entités désactivées", ss = "{count} plages ont des entités désactivées", cs = "Jours de la semaine", ls = "Positif : décharge, négatif : charge", us = "Positif : injection, négatif : soutirage", ds = "Positif : fournit, négatif : absorbe", fs = "Mode", ps = "Batterie", ms = "Réseau", hs = "Pilotage de puissance", gs = "Chargeur de VE", _s = "Appareil", vs = "Système", ys = "Afficher les chaînes solaires", bs = "Afficher l'équipement optionnel", xs = "Périmètre", Ss = "Ce système", Cs = "Système en parallèle", ws = "Afficher l'énergie du jour", Ts = "Afficher les groupes sans défaut", Es = "Afficher les modules de batterie", Ds = "Sections", Os = "Charge", ks = "Décharge", As = "Chargeur de VE", js = "Afficher la chronologie de la semaine", Ms = "Flux de puissance SAJ Local", Ns = "Puissance en direct entre le solaire, la batterie, le réseau, la maison et l'équipement optionnel", Ps = "État de SAJ Local", Fs = "État de fonctionnement, mode, mesures clés, énergie du jour, défauts et autorisation du contrôle", Is = "Défauts de SAJ Local", Ls = "Défauts actifs par équipement, avec effacement du défaut", Rs = "Batterie de SAJ Local", zs = "État de charge avec réserve et limites, mesures de la batterie et une ligne par module", Bs = "Contrôle de SAJ Local", Vs = "Les commandes communes que le système propose", Hs = "Programme de charge de SAJ Local", Us = "Plages de charge avec une chronologie de la semaine", Ws = "Programme de décharge de SAJ Local", Gs = "Plages de décharge avec une chronologie de la semaine", Ks = "Programme du chargeur de VE de SAJ Local", qs = "Plages du chargeur de VE avec une chronologie de la semaine", Js = "Jours de la semaine de SAJ Local", Ys = {
		choose_system: po,
		badge_name: mo,
		badge_description: ho,
		not_answering: go,
		unavailable: _o,
		busy: vo,
		press: yo,
		week_timeline: bo,
		locked_message: xo,
		open_settings: So,
		empty_title: Co,
		empty_enable: wo,
		open_device_page: To,
		entity_kind_reading: Eo,
		entity_kind_configuration: Do,
		entity_kind_schedule: Oo,
		solar: ko,
		battery: Ao,
		grid: jo,
		home: Mo,
		inverter: No,
		ev_charger: Po,
		backup_load: Fo,
		meter_b: Io,
		charging: Lo,
		discharging: Ro,
		importing: zo,
		exporting: Bo,
		idle: Vo,
		no_faults: Ho,
		faults: Uo,
		changes: Wo,
		battery_pack: Go,
		faults_count_one: Ko,
		faults_count_many: qo,
		faults_count_other: Jo,
		no_active_faults: Yo,
		clear_fault: Xo,
		see_diagnostics: Zo,
		changes_allowed: Qo,
		changes_off: $o,
		no_battery: es,
		mode: ts,
		mode_running_now: ns,
		time_of_use_notice: rs,
		slot_number: is,
		slots_left_out_one: as,
		slots_left_out_many: os,
		slots_left_out_other: ss,
		weekdays: cs,
		sign_battery: ls,
		sign_grid: us,
		sign_inverter: ds,
		section_mode: fs,
		section_battery: ps,
		section_grid: ms,
		section_power_control: hs,
		section_ev_charger: gs,
		section_device: _s,
		option_device: vs,
		option_show_strings: ys,
		option_show_optional_equipment: bs,
		option_scope: xs,
		option_scope_system: Ss,
		option_scope_parallel: Cs,
		option_show_energy: ws,
		option_show_groups_without_faults: Ts,
		option_show_packs: Es,
		option_sections: Ds,
		option_kind_charge: Os,
		option_kind_discharge: ks,
		option_kind_ev_charger: As,
		option_show_timeline: js,
		power_flow_card_name: Ms,
		power_flow_card_description: Ns,
		status_card_name: Ps,
		status_card_description: Fs,
		faults_card_name: Is,
		faults_card_description: Ls,
		battery_card_name: Rs,
		battery_card_description: zs,
		controls_card_name: Bs,
		controls_card_description: Vs,
		charge_schedule_card_name: Hs,
		charge_schedule_card_description: Us,
		discharge_schedule_card_name: Ws,
		discharge_schedule_card_description: Gs,
		ev_charger_schedule_card_name: Ks,
		ev_charger_schedule_card_description: qs,
		weekdays_feature_name: Js
	};
})), Zs, Qs, $s, ec, tc, nc, rc, ic, ac, oc, sc, cc, lc, uc, dc, fc, pc, mc, hc, gc, _c, vc, yc, bc, xc, Sc, Cc, wc, Tc, Ec, Dc, Oc, kc, Ac, jc, Mc, Nc, Pc, Fc, Ic, Lc, Rc, zc, Bc, Vc, Hc, Uc, Wc, Gc, Kc, qc, Jc, Yc, Xc, Zc, Qc, $c, el, tl, nl, rl, il, al, ol, sl, cl, ll, ul, dl, fl, pl, ml, hl, gl, _l, vl, yl, bl, xl, Sl, Cl, wl, Tl, El, Dl, Ol, kl, Al, jl, Ml, Nl, Pl = t((() => {
	Zs = "Scegli un sistema SAJ Local", Qs = "Stato di SAJ Local", $s = "Stato di funzionamento e numero di guasti attivi di un sistema SAJ Local", ec = "Non risponde", tc = "Non disponibile", nc = "In corso", rc = "Premi", ic = "Linea temporale settimanale", ac = "Il controllo è disattivato per questo sistema", oc = "Apri le impostazioni", sc = "Ancora nulla da mostrare", cc = "Abilita le entità di {kind} nella pagina del dispositivo del sistema per mostrarle qui.", lc = "Apri la pagina del dispositivo", uc = "lettura", dc = "configurazione", fc = "pianificazione", pc = "Solare", mc = "Batteria", hc = "Rete", gc = "Casa", _c = "Inverter", vc = "Caricatore EV", yc = "Carichi di backup", bc = "Contatore B", xc = "In carica", Sc = "In scarica", Cc = "Prelievo", wc = "Immissione", Tc = "Inattivo", Ec = "Nessun guasto", Dc = "Guasti", Oc = "Controllo", kc = "Modulo {number}", Ac = "{count} guasto", jc = "{count} guasti", Mc = "{count} guasti", Nc = "Nessun guasto attivo", Pc = "Cancella guasto", Fc = "Vedi il download diagnostica per il registro e il bit", Ic = "Controllo consentito", Lc = "Controllo disattivato", Rc = "Questo sistema non ha una batteria", zc = "Modalità", Bc = "In esecuzione ora", Vc = "Le fasce di carica e scarica funzionano solo nella modalità a fasce orarie", Hc = "Fascia {number}", Uc = "{count} fascia ha entità disabilitate", Wc = "{count} fasce hanno entità disabilitate", Gc = "{count} fasce hanno entità disabilitate", Kc = "Giorni della settimana", qc = "Positivo scarica, negativo carica", Jc = "Positivo immette, negativo preleva", Yc = "Positivo eroga, negativo assorbe", Xc = "Modalità", Zc = "Batteria", Qc = "Rete", $c = "Controllo della potenza", el = "Caricatore EV", tl = "Dispositivo", nl = "Sistema", rl = "Mostra le stringhe solari", il = "Mostra le apparecchiature opzionali", al = "Ambito", ol = "Questo sistema", sl = "Sistema in parallelo", cl = "Mostra l'energia di oggi", ll = "Mostra i gruppi senza guasti", ul = "Mostra i moduli batteria", dl = "Sezioni", fl = "Carica", pl = "Scarica", ml = "Caricatore EV", hl = "Mostra la linea temporale settimanale", gl = "Flusso di potenza SAJ Local", _l = "Potenza in tempo reale tra solare, batteria, rete, casa e apparecchiature opzionali", vl = "Stato SAJ Local", yl = "Stato di funzionamento, modalità, letture principali, energia di oggi, guasti e se il controllo è consentito", bl = "Guasti SAJ Local", xl = "Guasti attivi per ogni apparecchiatura, con cancellazione del guasto", Sl = "Batteria SAJ Local", Cl = "Stato di carica con riserva e limiti, letture della batteria e una riga per ogni modulo", wl = "Controlli SAJ Local", Tl = "I controlli condivisi offerti dal sistema", El = "Pianificazione di carica SAJ Local", Dl = "Fasce di carica con una linea temporale settimanale", Ol = "Pianificazione di scarica SAJ Local", kl = "Fasce di scarica con una linea temporale settimanale", Al = "Pianificazione del caricatore EV SAJ Local", jl = "Fasce del caricatore EV con una linea temporale settimanale", Ml = "Giorni della settimana SAJ Local", Nl = {
		choose_system: Zs,
		badge_name: Qs,
		badge_description: $s,
		not_answering: ec,
		unavailable: tc,
		busy: nc,
		press: rc,
		week_timeline: ic,
		locked_message: ac,
		open_settings: oc,
		empty_title: sc,
		empty_enable: cc,
		open_device_page: lc,
		entity_kind_reading: uc,
		entity_kind_configuration: dc,
		entity_kind_schedule: fc,
		solar: pc,
		battery: mc,
		grid: hc,
		home: gc,
		inverter: _c,
		ev_charger: vc,
		backup_load: yc,
		meter_b: bc,
		charging: xc,
		discharging: Sc,
		importing: Cc,
		exporting: wc,
		idle: Tc,
		no_faults: Ec,
		faults: Dc,
		changes: Oc,
		battery_pack: kc,
		faults_count_one: Ac,
		faults_count_many: jc,
		faults_count_other: Mc,
		no_active_faults: Nc,
		clear_fault: Pc,
		see_diagnostics: Fc,
		changes_allowed: Ic,
		changes_off: Lc,
		no_battery: Rc,
		mode: zc,
		mode_running_now: Bc,
		time_of_use_notice: Vc,
		slot_number: Hc,
		slots_left_out_one: Uc,
		slots_left_out_many: Wc,
		slots_left_out_other: Gc,
		weekdays: Kc,
		sign_battery: qc,
		sign_grid: Jc,
		sign_inverter: Yc,
		section_mode: Xc,
		section_battery: Zc,
		section_grid: Qc,
		section_power_control: $c,
		section_ev_charger: el,
		section_device: tl,
		option_device: nl,
		option_show_strings: rl,
		option_show_optional_equipment: il,
		option_scope: al,
		option_scope_system: ol,
		option_scope_parallel: sl,
		option_show_energy: cl,
		option_show_groups_without_faults: ll,
		option_show_packs: ul,
		option_sections: dl,
		option_kind_charge: fl,
		option_kind_discharge: pl,
		option_kind_ev_charger: ml,
		option_show_timeline: hl,
		power_flow_card_name: gl,
		power_flow_card_description: _l,
		status_card_name: vl,
		status_card_description: yl,
		faults_card_name: bl,
		faults_card_description: xl,
		battery_card_name: Sl,
		battery_card_description: Cl,
		controls_card_name: wl,
		controls_card_description: Tl,
		charge_schedule_card_name: El,
		charge_schedule_card_description: Dl,
		discharge_schedule_card_name: Ol,
		discharge_schedule_card_description: kl,
		ev_charger_schedule_card_name: Al,
		ev_charger_schedule_card_description: jl,
		weekdays_feature_name: Ml
	};
})), Fl, Il, Ll, Rl, zl, Bl, Vl, Hl, Ul, Wl, Gl, Kl, ql, Jl, Yl, Xl, Zl, Ql, $l, eu, tu, nu, ru, iu, au, ou, su, cu, lu, uu, du, fu, pu, mu, hu, gu, _u, vu, yu, bu, xu, Su, Cu, wu, Tu, Eu, Du, Ou, ku, Au, ju, Mu, Nu, Pu, Fu, Iu, Lu, Ru, zu, Bu, Vu, Hu, Uu, Wu, Gu, Ku, qu, Ju, Yu, Xu, Zu, Qu, $u, ed, td, nd, rd, id, ad, od, sd, cd, ld, ud, dd, fd, pd = t((() => {
	Fl = "Kies een SAJ Local-systeem", Il = "SAJ Local-status", Ll = "Bedrijfstoestand en aantal actieve storingen van een SAJ Local-systeem", Rl = "Antwoordt niet", zl = "Niet beschikbaar", Bl = "Bezig", Vl = "Indrukken", Hl = "Weektijdlijn", Ul = "Bediening is uitgeschakeld voor dit systeem", Wl = "Instellingen openen", Gl = "Nog niets om te tonen", Kl = "Schakel {kind}-entiteiten in op de apparaatpagina van het systeem om ze hier te tonen.", ql = "Apparaatpagina openen", Jl = "meting", Yl = "configuratie", Xl = "schema", Zl = "Batterij", Ql = "Huis", $l = "Omvormer", eu = "EV-lader", tu = "Back-upbelasting", nu = "Meter B", ru = "Opladen", iu = "Ontladen", au = "Afname", ou = "Teruglevering", su = "Inactief", cu = "Geen storingen", lu = "Storingen", uu = "Bediening", du = "Pack {number}", fu = "{count} storing", pu = "{count} storingen", mu = "Geen actieve storingen", hu = "Storing wissen", gu = "Zie de diagnosedownload voor het register en de bit", _u = "Bediening toegestaan", vu = "Bediening uit", yu = "Dit systeem heeft geen batterij", bu = "Modus", xu = "Nu actief", Su = "Oplaad- en ontlaadtijdvakken worden alleen uitgevoerd in de tijdgestuurde modus", Cu = "Tijdvak {number}", wu = "{count} tijdvak heeft uitgeschakelde entiteiten", Tu = "{count} tijdvakken hebben uitgeschakelde entiteiten", Eu = "Dagen van de week", Du = "Positief ontlaadt, negatief laadt op", Ou = "Positief levert terug, negatief neemt af", ku = "Positief levert af, negatief neemt op", Au = "Modus", ju = "Batterij", Mu = "Vermogensregeling", Nu = "EV-lader", Pu = "Apparaat", Fu = "Systeem", Iu = "Zonnestrings tonen", Lu = "Optionele apparatuur tonen", Ru = "Bereik", zu = "Dit systeem", Bu = "Parallel systeem", Vu = "Energie van vandaag tonen", Hu = "Groepen zonder storingen tonen", Uu = "Batterijpacks tonen", Wu = "Secties", Gu = "Opladen", Ku = "Ontladen", qu = "EV-lader", Ju = "Weektijdlijn tonen", Yu = "SAJ Local-vermogensstroom", Xu = "Live vermogen tussen zon, batterij, net, huis en de optionele apparatuur", Zu = "SAJ Local-status", Qu = "Bedrijfstoestand, modus, belangrijke metingen, energie van vandaag, storingen en of bediening is toegestaan", $u = "SAJ Local-storingen", ed = "Actieve storingen per onderdeel van de apparatuur, met storing wissen", td = "SAJ Local-batterij", nd = "Laadniveau met reserve en limieten, batterijmetingen en één rij per pack", rd = "SAJ Local-bediening", id = "De gedeelde bediening die het systeem biedt", ad = "SAJ Local-oplaadschema", od = "Oplaadtijdvakken met een weektijdlijn", sd = "SAJ Local-ontlaadschema", cd = "Ontlaadtijdvakken met een weektijdlijn", ld = "SAJ Local-EV-laderschema", ud = "EV-ladertijdvakken met een weektijdlijn", dd = "SAJ Local-weekdagen", fd = {
		choose_system: Fl,
		badge_name: Il,
		badge_description: Ll,
		not_answering: Rl,
		unavailable: zl,
		busy: Bl,
		press: Vl,
		week_timeline: Hl,
		locked_message: Ul,
		open_settings: Wl,
		empty_title: Gl,
		empty_enable: Kl,
		open_device_page: ql,
		entity_kind_reading: Jl,
		entity_kind_configuration: Yl,
		entity_kind_schedule: Xl,
		solar: "Zon",
		battery: Zl,
		grid: "Net",
		home: Ql,
		inverter: $l,
		ev_charger: eu,
		backup_load: tu,
		meter_b: nu,
		charging: ru,
		discharging: iu,
		importing: au,
		exporting: ou,
		idle: su,
		no_faults: cu,
		faults: lu,
		changes: uu,
		battery_pack: du,
		faults_count_one: fu,
		faults_count_other: pu,
		no_active_faults: mu,
		clear_fault: hu,
		see_diagnostics: gu,
		changes_allowed: _u,
		changes_off: vu,
		no_battery: yu,
		mode: bu,
		mode_running_now: xu,
		time_of_use_notice: Su,
		slot_number: Cu,
		slots_left_out_one: wu,
		slots_left_out_other: Tu,
		weekdays: Eu,
		sign_battery: Du,
		sign_grid: Ou,
		sign_inverter: ku,
		section_mode: Au,
		section_battery: ju,
		section_grid: "Net",
		section_power_control: Mu,
		section_ev_charger: Nu,
		section_device: Pu,
		option_device: Fu,
		option_show_strings: Iu,
		option_show_optional_equipment: Lu,
		option_scope: Ru,
		option_scope_system: zu,
		option_scope_parallel: Bu,
		option_show_energy: Vu,
		option_show_groups_without_faults: Hu,
		option_show_packs: Uu,
		option_sections: Wu,
		option_kind_charge: Gu,
		option_kind_discharge: Ku,
		option_kind_ev_charger: qu,
		option_show_timeline: Ju,
		power_flow_card_name: Yu,
		power_flow_card_description: Xu,
		status_card_name: Zu,
		status_card_description: Qu,
		faults_card_name: $u,
		faults_card_description: ed,
		battery_card_name: td,
		battery_card_description: nd,
		controls_card_name: rd,
		controls_card_description: id,
		charge_schedule_card_name: ad,
		charge_schedule_card_description: od,
		discharge_schedule_card_name: sd,
		discharge_schedule_card_description: cd,
		ev_charger_schedule_card_name: ld,
		ev_charger_schedule_card_description: ud,
		weekdays_feature_name: dd
	};
})), md, hd, gd, _d, vd, yd, bd, xd, Sd, Cd, wd, Td, Ed, Dd, Od, kd, Ad, jd, Md, Nd, Pd, Fd, Id, Ld, Rd, zd, Bd, Vd, Hd, Ud, Wd, Gd, Kd, qd, Jd, Yd, Xd, Zd, Qd, $d, ef, tf, nf, rf, af, of, sf, cf, lf, uf, df, ff, pf, mf, hf, gf, _f, vf, yf, bf, xf, Sf, Cf, wf, Tf, Ef, Df, Of, kf, Af, jf, Mf, Nf, Pf, Ff, If, Lf, Rf, zf, Bf, Vf, Hf, Uf, Wf, Gf, Kf, qf, Jf, Yf, Xf, Zf, Qf, $f = t((() => {
	md = "Wybierz system SAJ Local", hd = "Stan SAJ Local", gd = "Stan pracy i liczba aktywnych usterek systemu SAJ Local", _d = "Nie odpowiada", vd = "Niedostępny", yd = "Pracuje", bd = "Naciśnij", xd = "Oś czasu tygodnia", Sd = "Sterowanie jest wyłączone dla tego systemu", Cd = "Otwórz ustawienia", wd = "Nie ma jeszcze nic do pokazania", Td = "Włącz encje typu {kind} na stronie urządzenia systemu, aby pokazać je tutaj.", Ed = "Otwórz stronę urządzenia", Dd = "odczyt", Od = "konfiguracja", kd = "harmonogram", Ad = "Słońce", jd = "Bateria", Md = "Sieć", Nd = "Falownik", Pd = "Ładowarka EV", Fd = "Odbiory awaryjne", Id = "Licznik B", Ld = "Ładowanie", Rd = "Rozładowanie", zd = "Pobór", Bd = "Oddawanie", Vd = "Bezczynny", Hd = "Brak usterek", Ud = "Usterki", Wd = "Sterowanie", Gd = "Moduł {number}", Kd = "{count} usterka", qd = "{count} usterki", Jd = "{count} usterek", Yd = "{count} usterki", Xd = "Brak aktywnych usterek", Zd = "Wyczyść usterkę", Qd = "Rejestr i bit znajdziesz w pobranej diagnostyce", $d = "Sterowanie dozwolone", ef = "Sterowanie wyłączone", tf = "Ten system nie ma baterii", nf = "Tryb", rf = "Działa teraz", af = "Przedziały ładowania i rozładowania działają tylko w trybie taryfy czasowej", of = "Przedział {number}", sf = "{count} przedział ma wyłączone encje", cf = "{count} przedziały mają wyłączone encje", lf = "{count} przedziałów ma wyłączone encje", uf = "{count} przedziału ma wyłączone encje", df = "Dni tygodnia", ff = "Wartość dodatnia rozładowuje, ujemna ładuje", pf = "Wartość dodatnia oddaje, ujemna pobiera", mf = "Wartość dodatnia oddaje moc, ujemna ją pobiera", hf = "Tryb", gf = "Bateria", _f = "Sieć", vf = "Sterowanie mocą", yf = "Ładowarka EV", bf = "Urządzenie", xf = "System", Sf = "Pokaż ciągi paneli", Cf = "Pokaż wyposażenie opcjonalne", wf = "Zakres", Tf = "Ten system", Ef = "System równoległy", Df = "Pokaż dzisiejszą energię", Of = "Pokaż grupy bez usterek", kf = "Pokaż moduły baterii", Af = "Sekcje", jf = "Ładowanie", Mf = "Rozładowanie", Nf = "Ładowarka EV", Pf = "Pokaż oś czasu tygodnia", Ff = "Przepływ mocy SAJ Local", If = "Bieżący przepływ mocy między słońcem, baterią, siecią, domem i wyposażeniem opcjonalnym", Lf = "Stan SAJ Local", Rf = "Stan pracy, tryb, kluczowe odczyty, dzisiejsza energia, usterki i informacja, czy sterowanie jest dozwolone", zf = "Usterki SAJ Local", Bf = "Aktywne usterki według elementu wyposażenia, z przyciskiem Wyczyść usterkę", Vf = "Bateria SAJ Local", Hf = "Stan naładowania z rezerwą i limitami, odczyty baterii i jeden wiersz dla każdego modułu", Uf = "Sterowanie SAJ Local", Wf = "Wspólne elementy sterowania, które oferuje system", Gf = "Harmonogram ładowania SAJ Local", Kf = "Przedziały ładowania z osią czasu tygodnia", qf = "Harmonogram rozładowania SAJ Local", Jf = "Przedziały rozładowania z osią czasu tygodnia", Yf = "Harmonogram ładowarki EV SAJ Local", Xf = "Przedziały ładowarki EV z osią czasu tygodnia", Zf = "Dni tygodnia SAJ Local", Qf = {
		choose_system: md,
		badge_name: hd,
		badge_description: gd,
		not_answering: _d,
		unavailable: vd,
		busy: yd,
		press: bd,
		week_timeline: xd,
		locked_message: Sd,
		open_settings: Cd,
		empty_title: wd,
		empty_enable: Td,
		open_device_page: Ed,
		entity_kind_reading: Dd,
		entity_kind_configuration: Od,
		entity_kind_schedule: kd,
		solar: Ad,
		battery: jd,
		grid: Md,
		home: "Dom",
		inverter: Nd,
		ev_charger: Pd,
		backup_load: Fd,
		meter_b: Id,
		charging: Ld,
		discharging: Rd,
		importing: zd,
		exporting: Bd,
		idle: Vd,
		no_faults: Hd,
		faults: Ud,
		changes: Wd,
		battery_pack: Gd,
		faults_count_one: Kd,
		faults_count_few: qd,
		faults_count_many: Jd,
		faults_count_other: Yd,
		no_active_faults: Xd,
		clear_fault: Zd,
		see_diagnostics: Qd,
		changes_allowed: $d,
		changes_off: ef,
		no_battery: tf,
		mode: nf,
		mode_running_now: rf,
		time_of_use_notice: af,
		slot_number: of,
		slots_left_out_one: sf,
		slots_left_out_few: cf,
		slots_left_out_many: lf,
		slots_left_out_other: uf,
		weekdays: df,
		sign_battery: ff,
		sign_grid: pf,
		sign_inverter: mf,
		section_mode: hf,
		section_battery: gf,
		section_grid: _f,
		section_power_control: vf,
		section_ev_charger: yf,
		section_device: bf,
		option_device: xf,
		option_show_strings: Sf,
		option_show_optional_equipment: Cf,
		option_scope: wf,
		option_scope_system: Tf,
		option_scope_parallel: Ef,
		option_show_energy: Df,
		option_show_groups_without_faults: Of,
		option_show_packs: kf,
		option_sections: Af,
		option_kind_charge: jf,
		option_kind_discharge: Mf,
		option_kind_ev_charger: Nf,
		option_show_timeline: Pf,
		power_flow_card_name: Ff,
		power_flow_card_description: If,
		status_card_name: Lf,
		status_card_description: Rf,
		faults_card_name: zf,
		faults_card_description: Bf,
		battery_card_name: Vf,
		battery_card_description: Hf,
		controls_card_name: Uf,
		controls_card_description: Wf,
		charge_schedule_card_name: Gf,
		charge_schedule_card_description: Kf,
		discharge_schedule_card_name: qf,
		discharge_schedule_card_description: Jf,
		ev_charger_schedule_card_name: Yf,
		ev_charger_schedule_card_description: Xf,
		weekdays_feature_name: Zf
	};
})), ep, tp, np, rp, ip, ap, op, sp, cp, lp, up, dp, fp, pp, mp, hp, gp, _p, vp, yp, bp, xp, Sp, Cp, wp, Tp, Ep, Dp, Op, kp, Ap, jp, Mp, Np, Pp, Fp, Ip, Lp, Rp, zp, Bp, Vp, Hp, Up, Wp, Gp, Kp, qp, Jp, Yp, Xp, Zp, Qp, $p, em, tm, nm, rm, im, am, om, sm, cm, lm, um, dm, fm, pm, mm, hm, gm, _m, vm, ym, bm, xm, Sm, Cm, wm, Tm, Em, Dm, Om, km, Am, jm, Mm = t((() => {
	ep = "Välj ett SAJ Local-system", tp = "SAJ Local-status", np = "Driftläge och antal aktiva fel för ett SAJ Local-system", rp = "Svarar inte", ip = "Otillgänglig", ap = "Arbetar", op = "Tryck", sp = "Veckotidslinje", cp = "Styrning är av för det här systemet", lp = "Öppna inställningar", up = "Inget att visa ännu", dp = "Aktivera entiteterna för {kind} på systemets enhetssida för att visa dem här.", fp = "Öppna enhetssidan", pp = "avläsning", mp = "konfiguration", hp = "schema", gp = "Batteri", _p = "Nät", vp = "Växelriktare", yp = "Elbilsladdare", bp = "Reservlast", xp = "Mätare B", Sp = "Laddar", Cp = "Laddar ur", wp = "Import", Tp = "Export", Ep = "Overksam", Dp = "Inga fel", Op = "Styrning", kp = "Pack {number}", Ap = "{count} fel", jp = "{count} fel", Mp = "Inga aktiva fel", Np = "Rensa fel", Pp = "Se diagnostiknedladdningen för register och bit", Fp = "Styrning tillåten", Ip = "Styrning av", Lp = "Det här systemet har inget batteri", Rp = "Läge", zp = "Körs nu", Bp = "Tidsluckor för laddning och urladdning körs bara i läget tidsstyrning", Vp = "Tidslucka {number}", Hp = "{count} tidslucka har inaktiverade entiteter", Up = "{count} tidsluckor har inaktiverade entiteter", Wp = "Veckodagar", Gp = "Positivt laddar ur, negativt laddar", Kp = "Positivt exporterar, negativt importerar", qp = "Positivt avger, negativt tar in", Jp = "Läge", Yp = "Batteri", Xp = "Nät", Zp = "Effektstyrning", Qp = "Elbilsladdare", $p = "Enhet", em = "System", tm = "Visa solcellssträngar", nm = "Visa valfri utrustning", rm = "Omfång", im = "Det här systemet", am = "Parallellsystem", om = "Visa dagens energi", sm = "Visa grupper utan fel", cm = "Visa batteripack", lm = "Sektioner", um = "Laddning", dm = "Urladdning", fm = "Elbilsladdare", pm = "Visa veckotidslinje", mm = "SAJ Local effektflöde", hm = "Live-effekt mellan sol, batteri, nät, hem och den valfria utrustningen", gm = "SAJ Local-status", _m = "Driftläge, läge, viktiga avläsningar, dagens energi, fel och om styrning är tillåten", vm = "SAJ Local-fel", ym = "Aktiva fel per utrustning, med rensa fel", bm = "SAJ Local-batteri", xm = "Laddningsnivå med reserv och gränser, batteriavläsningar och en rad per pack", Sm = "SAJ Local-styrning", Cm = "De gemensamma styrningarna som systemet erbjuder", wm = "SAJ Local-laddningsschema", Tm = "Tidsluckor för laddning med en veckotidslinje", Em = "SAJ Local-urladdningsschema", Dm = "Tidsluckor för urladdning med en veckotidslinje", Om = "SAJ Local-elbilsladdarschema", km = "Tidsluckor för elbilsladdare med en veckotidslinje", Am = "SAJ Local-veckodagar", jm = {
		choose_system: ep,
		badge_name: tp,
		badge_description: np,
		not_answering: rp,
		unavailable: ip,
		busy: ap,
		press: op,
		week_timeline: sp,
		locked_message: cp,
		open_settings: lp,
		empty_title: up,
		empty_enable: dp,
		open_device_page: fp,
		entity_kind_reading: pp,
		entity_kind_configuration: mp,
		entity_kind_schedule: hp,
		solar: "Sol",
		battery: gp,
		grid: _p,
		home: "Hem",
		inverter: vp,
		ev_charger: yp,
		backup_load: bp,
		meter_b: xp,
		charging: Sp,
		discharging: Cp,
		importing: wp,
		exporting: Tp,
		idle: Ep,
		no_faults: Dp,
		faults: "Fel",
		changes: Op,
		battery_pack: kp,
		faults_count_one: Ap,
		faults_count_other: jp,
		no_active_faults: Mp,
		clear_fault: Np,
		see_diagnostics: Pp,
		changes_allowed: Fp,
		changes_off: Ip,
		no_battery: Lp,
		mode: Rp,
		mode_running_now: zp,
		time_of_use_notice: Bp,
		slot_number: Vp,
		slots_left_out_one: Hp,
		slots_left_out_other: Up,
		weekdays: Wp,
		sign_battery: Gp,
		sign_grid: Kp,
		sign_inverter: qp,
		section_mode: Jp,
		section_battery: Yp,
		section_grid: Xp,
		section_power_control: Zp,
		section_ev_charger: Qp,
		section_device: $p,
		option_device: em,
		option_show_strings: tm,
		option_show_optional_equipment: nm,
		option_scope: rm,
		option_scope_system: im,
		option_scope_parallel: am,
		option_show_energy: om,
		option_show_groups_without_faults: sm,
		option_show_packs: cm,
		option_sections: lm,
		option_kind_charge: um,
		option_kind_discharge: dm,
		option_kind_ev_charger: fm,
		option_show_timeline: pm,
		power_flow_card_name: mm,
		power_flow_card_description: hm,
		status_card_name: gm,
		status_card_description: _m,
		faults_card_name: vm,
		faults_card_description: ym,
		battery_card_name: bm,
		battery_card_description: xm,
		controls_card_name: Sm,
		controls_card_description: Cm,
		charge_schedule_card_name: wm,
		charge_schedule_card_description: Tm,
		discharge_schedule_card_name: Em,
		discharge_schedule_card_description: Dm,
		ev_charger_schedule_card_name: Om,
		ev_charger_schedule_card_description: km,
		weekdays_feature_name: Am
	};
})), Nm, Pm, Fm, Im, Lm, Rm, zm, Bm, Vm, Hm, Um, Wm, Gm, Km, qm, Jm, Ym, Xm, Zm, Qm, $m, eh, th, nh, rh, ih, ah, oh, sh, ch, lh, uh, dh, fh, ph, mh, hh, gh, _h, vh, yh, bh, xh, Sh, Ch, wh, Th, Eh, Dh, Oh, kh, Ah, jh, Mh, Nh, Ph, Fh, Ih, Lh, Rh, zh, Bh, Vh, Hh, Uh, Wh, Gh, Kh, qh, Jh, Yh, Xh, Zh, Qh, $h, eg, tg, ng, rg, ig, ag, og, sg, cg, lg, ug, dg, fg = t((() => {
	Nm = "选择一个 SAJ Local 系统", Pm = "SAJ Local 状态", Fm = "SAJ Local 系统的运行状态和当前故障数量", Im = "无响应", Lm = "不可用", Rm = "处理中", zm = "按下", Bm = "一周时间线", Vm = "此系统的控制已关闭", Hm = "打开设置", Um = "暂无内容可显示", Wm = "在系统的设备页面启用{kind}实体，即可在此显示。", Gm = "打开设备页面", Km = "读数", qm = "配置", Jm = "计划", Ym = "光伏", Xm = "电池", Zm = "电网", Qm = "家庭", $m = "逆变器", eh = "充电桩", th = "备用负载", nh = "电表 B", rh = "充电", ih = "放电", ah = "购电", oh = "馈电", sh = "空闲", ch = "无故障", lh = "故障", uh = "控制", dh = "电池包 {number}", fh = "{count} 个故障", ph = "无当前故障", mh = "清除故障", hh = "寄存器和位请查看诊断下载", gh = "允许控制", _h = "控制已关闭", vh = "此系统没有电池", yh = "模式", bh = "当前运行", xh = "充电和放电时段只在分时模式下运行", Sh = "时段 {number}", Ch = "{count} 个时段有已禁用的实体", wh = "星期", Th = "正值为放电，负值为充电", Eh = "正值为馈电，负值为购电", Dh = "正值为输出，负值为输入", Oh = "模式", kh = "电池", Ah = "电网", jh = "功率控制", Mh = "充电桩", Nh = "设备", Ph = "系统", Fh = "显示光伏组串", Ih = "显示可选设备", Lh = "范围", Rh = "此系统", zh = "并机系统", Bh = "显示今日电量", Vh = "显示无故障的分组", Hh = "显示电池包", Uh = "分区", Wh = "充电", Gh = "放电", Kh = "充电桩", qh = "显示一周时间线", Jh = "SAJ Local 功率流", Yh = "光伏、电池、电网、家庭和可选设备之间的实时功率", Xh = "SAJ Local 状态", Zh = "运行状态、模式、关键读数、今日电量、故障，以及是否允许控制", Qh = "SAJ Local 故障", $h = "按设备列出当前故障，并可清除故障", eg = "SAJ Local 电池", tg = "荷电状态、备用电量和限制、电池读数，以及每个电池包一行", ng = "SAJ Local 控制", rg = "系统提供的共用控制项", ig = "SAJ Local 充电计划", ag = "充电时段，附一周时间线", og = "SAJ Local 放电计划", sg = "放电时段，附一周时间线", cg = "SAJ Local 充电桩计划", lg = "充电桩时段，附一周时间线", ug = "SAJ Local 星期", dg = {
		choose_system: Nm,
		badge_name: Pm,
		badge_description: Fm,
		not_answering: Im,
		unavailable: Lm,
		busy: Rm,
		press: zm,
		week_timeline: Bm,
		locked_message: Vm,
		open_settings: Hm,
		empty_title: Um,
		empty_enable: Wm,
		open_device_page: Gm,
		entity_kind_reading: Km,
		entity_kind_configuration: qm,
		entity_kind_schedule: Jm,
		solar: Ym,
		battery: Xm,
		grid: Zm,
		home: Qm,
		inverter: $m,
		ev_charger: eh,
		backup_load: th,
		meter_b: nh,
		charging: rh,
		discharging: ih,
		importing: ah,
		exporting: oh,
		idle: sh,
		no_faults: ch,
		faults: lh,
		changes: uh,
		battery_pack: dh,
		faults_count_other: fh,
		no_active_faults: ph,
		clear_fault: mh,
		see_diagnostics: hh,
		changes_allowed: gh,
		changes_off: _h,
		no_battery: vh,
		mode: yh,
		mode_running_now: bh,
		time_of_use_notice: xh,
		slot_number: Sh,
		slots_left_out_other: Ch,
		weekdays: wh,
		sign_battery: Th,
		sign_grid: Eh,
		sign_inverter: Dh,
		section_mode: Oh,
		section_battery: kh,
		section_grid: Ah,
		section_power_control: jh,
		section_ev_charger: Mh,
		section_device: Nh,
		option_device: Ph,
		option_show_strings: Fh,
		option_show_optional_equipment: Ih,
		option_scope: Lh,
		option_scope_system: Rh,
		option_scope_parallel: zh,
		option_show_energy: Bh,
		option_show_groups_without_faults: Vh,
		option_show_packs: Hh,
		option_sections: Uh,
		option_kind_charge: Wh,
		option_kind_discharge: Gh,
		option_kind_ev_charger: Kh,
		option_show_timeline: qh,
		power_flow_card_name: Jh,
		power_flow_card_description: Yh,
		status_card_name: Xh,
		status_card_description: Zh,
		faults_card_name: Qh,
		faults_card_description: $h,
		battery_card_name: eg,
		battery_card_description: tg,
		controls_card_name: ng,
		controls_card_description: rg,
		charge_schedule_card_name: ig,
		charge_schedule_card_description: ag,
		discharge_schedule_card_name: og,
		discharge_schedule_card_description: sg,
		ev_charger_schedule_card_name: cg,
		ev_charger_schedule_card_description: lg,
		weekdays_feature_name: ug
	};
})), pg, mg, hg, gg, _g, vg, yg, bg, k, xg, Sg, Cg = t((() => {
	qn(), ki(), fo(), Xs(), Pl(), pd(), $f(), Mm(), fg(), pg = /* #__PURE__ */ Object.assign({
		"./de.json": Kn,
		"./en.json": Oi,
		"./es.json": uo,
		"./fr.json": Ys,
		"./it.json": Nl,
		"./nl.json": fd,
		"./pl.json": Qf,
		"./sv.json": jm,
		"./zh-Hans.json": dg
	}), mg = /^\.\/|\.json$/g, hg = () => new Map(Object.entries(pg).map(([e, t]) => [e.replace(mg, "").toLowerCase(), t])), gg = ({ language: e, available: t }) => {
		let n = e.toLowerCase().replaceAll("_", "-");
		return [n, n.replace(/-.*$/, "")].find((e) => t.has(e)) ?? "en";
	}, _g = ({ template: e, values: t }) => e.replace(/\{(\w+)\}/g, (e, n) => n in t ? String(t[n]) : e), vg = ({ language: e, available: t }) => {
		let n = t.get(gg({
			language: e,
			available: t
		})), r = t.get("en"), i = new Intl.PluralRules(e), a = (e) => n?.[e] ?? r?.[e];
		return (e, t = {}) => {
			let n = t.count, r = typeof n == "number" ? `${e}_${i.select(n)}` : void 0, o = (r === void 0 ? void 0 : a(r)) ?? a(e) ?? e;
			return _g({
				template: o,
				values: t
			});
		};
	}, yg = /* @__PURE__ */ new Map(), bg = (e) => {
		let t = yg.get(e);
		if (t !== void 0) return t;
		let n = vg({
			language: e,
			available: hg()
		});
		return yg.set(e, n), n;
	}, k = () => bg(document.documentElement.lang || "en"), xg = [
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
	], Sg = ({ from: e, now: t, language: n }) => {
		let r = Math.round((e.getTime() - t.getTime()) / 1e3), i = new Intl.RelativeTimeFormat(n, { numeric: "auto" }), a = xg.find((e) => Math.abs(r) >= e.seconds);
		return a === void 0 ? i.format(r, "second") : i.format(Math.round(r / a.seconds), a.name);
	};
})), wg, Tg, Eg, Dg, Og, kg, A, Ag, j, jg, M, N, P = t((() => {
	wg = "saj_local", Tg = "unavailable", Eg = "unknown", Dg = (e) => e.platform === "saj_local" && e.device_id !== null && typeof e.translation_key == "string" && e.translation_key !== "", Og = (e) => {
		let t = new Set(Object.values(e.entities).filter(Dg).map((e) => e.device_id));
		return Object.values(e.devices).filter((e) => t.has(e.id));
	}, kg = ({ hass: e, deviceId: t }) => Object.values(e.entities).filter((e) => Dg(e) && e.device_id === t).map((e) => e.entity_id), A = ({ hass: e, deviceId: t }) => {
		let n = /* @__PURE__ */ new Map();
		for (let r of Object.values(e.entities)) {
			let i = e.states[r.entity_id];
			Dg(r) && r.device_id === t && i !== void 0 && n.set(r.translation_key, {
				key: r.translation_key,
				entityId: r.entity_id,
				domain: r.entity_id.replace(/\..*$/, ""),
				state: i
			});
		}
		return n;
	}, Ag = ({ hass: e, entityId: t }) => {
		let n = e.entities[t];
		return n === void 0 || !Dg(n) ? null : {
			deviceId: n.device_id,
			key: n.translation_key
		};
	}, j = (e) => e.state.state === Tg, jg = (e) => e.length > 0 && e.every(j), M = (e) => {
		let { state: t } = e.state;
		if (t === Tg || t === Eg || t === "") return null;
		let n = Number(t);
		return Number.isFinite(n) ? n : null;
	}, N = (e) => e?.state.state === "on";
})), F, Mg, Ng, I, L, R = t((() => {
	Cg(), P(), F = ({ name: e, fallback: t }) => ({
		name: e,
		default: t,
		selector: { boolean: {} }
	}), Mg = ({ name: e, options: t, fallback: n }) => ({
		name: e,
		default: n,
		selector: { select: {
			options: t,
			mode: "dropdown"
		} }
	}), Ng = {
		name: "device",
		required: !0,
		selector: { device: { filter: { integration: wg } } }
	}, I = (e) => {
		let t = k();
		return {
			schema: [Ng, ...e(t)],
			computeLabel: (e) => t(`option_${e.name}`)
		};
	}, L = (e) => {
		let [t] = Og(e);
		return t === void 0 ? {} : { device: t.id };
	};
})), z, Pg, Fg, B = t((() => {
	Cg(), z = ({ type: e, nameKey: t, descriptionKey: n, preview: r }) => {
		window.customCards ??= [], window.customCards.push({
			type: e,
			preview: r,
			get name() {
				return k()(t);
			},
			get description() {
				return k()(n);
			}
		});
	}, Pg = ({ type: e, nameKey: t, isSupported: n, configurable: r }) => {
		window.customCardFeatures ??= [], window.customCardFeatures.push({
			type: e,
			isSupported: n,
			configurable: r,
			get name() {
				return k()(t);
			}
		});
	}, Fg = ({ type: e, nameKey: t, descriptionKey: n }) => {
		window.customBadges ??= [], window.customBadges.push({
			type: e,
			get name() {
				return k()(t);
			},
			get description() {
				return k()(n);
			}
		});
	};
})), V, Ig, Lg, Rg, zg, Bg, Vg = t((() => {
	P(), V = [
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
	], Ig = /^battery_pack\d+_(fault|warning)$/, Lg = "_fault_unrecognised", Rg = ({ definition: e, key: t }) => t.startsWith(`${e.prefix}_fault_`) || e.id === "battery" && Ig.test(t), zg = (e) => V.flatMap((t) => {
		let n = e.get(t.summaryKey);
		if (n === void 0) return [];
		let r = [...e.values()].filter((e) => e.domain === "binary_sensor" && N(e) && Rg({
			definition: t,
			key: e.key
		})).sort((e, t) => e.key.localeCompare(t.key)).map((e) => ({
			entity: e,
			since: new Date(e.state.last_changed),
			unrecognised: e.key.endsWith(Lg)
		}));
		return [{
			id: t.id,
			summary: n,
			active: N(n),
			rows: r
		}];
	}), Bg = (e) => V.flatMap((t) => {
		let n = e.get(t.summaryKey);
		return n !== void 0 && N(n) ? [n] : [];
	});
})), Hg, Ug, Wg = t((() => {
	Hg = new Map(Object.entries({
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
	})), Ug = (e) => Hg.get(e ?? "") ?? "disabled";
})), Gg, Kg, qg, Jg, Yg, Xg, Zg, Qg, $g, e_, t_, n_, r_, i_, a_, o_, s_, c_, l_ = t((() => {
	Gg = "M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", Kg = "M16.67,4H15V2H9V4H7.33A1.33,1.33 0 0,0 6,5.33V20.67C6,21.4 6.6,22 7.33,22H16.67A1.33,1.33 0 0,0 18,20.67V5.33C18,4.6 17.4,4 16.67,4Z", qg = "M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z", Jg = "M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z", Yg = "M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z", Xg = "M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z", Zg = "M12.43 11C12.28 10.84 10 7 7 7S2.32 10.18 2 11V13H11.57C11.72 13.16 14 17 17 17S21.68 13.82 22 13V11H12.43M7 9C8.17 9 9.18 9.85 10 11H4.31C4.78 10.17 5.54 9 7 9M17 15C15.83 15 14.82 14.15 14 13H19.69C19.22 13.83 18.46 15 17 15Z", Qg = "M19.77,7.23L19.78,7.22L16.06,3.5L15,4.56L17.11,6.67C16.17,7.03 15.5,7.93 15.5,9A2.5,2.5 0 0,0 18,11.5C18.36,11.5 18.69,11.42 19,11.29V18.5A1,1 0 0,1 18,19.5A1,1 0 0,1 17,18.5V14A2,2 0 0,0 15,12H14V5A2,2 0 0,0 12,3H6A2,2 0 0,0 4,5V21H14V13.5H15.5V18.5A2.5,2.5 0 0,0 18,21A2.5,2.5 0 0,0 20.5,18.5V9C20.5,8.31 20.22,7.68 19.77,7.23M18,10A1,1 0 0,1 17,9A1,1 0 0,1 18,8A1,1 0 0,1 19,9A1,1 0 0,1 18,10M8,18V13.5H6L10,6V11H12L8,18Z", $g = "M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z", e_ = "M12 20L5 20V12H2L12 3L14.78 5.5H14V7.17C12.84 7.58 12 8.7 12 10V20M15 9H16V7.5H20V9H21C21.55 9 22 9.45 22 10V21C22 21.55 21.55 22 21 22H15C14.45 22 14 21.55 14 21V10C14 9.45 14.45 9 15 9M16 11V14H20V11H16Z", t_ = "M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", n_ = "M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z", r_ = "M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z", i_ = "M12 2C7.04 2 3 6.04 3 11C3 14.91 5.5 18.24 9 19.47V22H11V19.94C11.33 20 11.66 20 12 20S12.67 20 13 19.94V22H15V19.47C18.5 18.23 21 14.9 21 11C21 6.04 16.96 2 12 2M14.25 14L11.25 17L9.75 15.5L11 14.25L9.75 13L12.75 10L14.25 11.5L13 12.75L14.25 14M16 9H8V7H16V9Z", a_ = "M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13", o_ = "M11.45,2V5.55L15,3.77L11.45,2M10.45,8L8,10.46L11.75,11.71L10.45,8M2,11.45L3.77,15L5.55,11.45H2M10,2H2V10C2.57,10.17 3.17,10.25 3.77,10.25C7.35,10.26 10.26,7.35 10.27,3.75C10.26,3.16 10.17,2.57 10,2M17,22V16H14L19,7V13H22L17,22Z", s_ = "M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z", c_ = "M8.28,5.45L6.5,4.55L7.76,2H16.23L17.5,4.55L15.72,5.44L15,4H9L8.28,5.45M18.62,8H14.09L13.3,5H10.7L9.91,8H5.38L4.1,10.55L5.89,11.44L6.62,10H17.38L18.1,11.45L19.89,10.56L18.62,8M17.77,22H15.7L15.46,21.1L12,15.9L8.53,21.1L8.3,22H6.23L9.12,11H11.19L10.83,12.35L12,14.1L13.16,12.35L12.81,11H14.88L17.77,22M11.4,15L10.5,13.65L9.32,18.13L11.4,15M14.68,18.12L13.5,13.64L12.6,15L14.68,18.12Z";
})), u_, d_ = t((() => {
	l_(), u_ = {
		solar: o_,
		battery: Kg,
		grid: c_,
		home: $g,
		inverter: Zg,
		ev: Qg,
		backup: e_,
		meter: i_,
		fault: Gg,
		ok: qg,
		lock: r_,
		settings: Xg,
		temperature: s_,
		clock: Yg,
		power: a_,
		info: t_,
		busy: n_,
		expand: Jg
	};
})), f_, H = t((() => {
	D(), d_(), f_ = class extends E {
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
			return S`<svg viewBox="0 0 24 24" aria-hidden="true"><path d=${u_[this.name]}></path></svg>`;
		}
	}, customElements.define("saj-icon", f_);
})), p_, m_ = t((() => {
	P(), p_ = class {
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
			return (this.registry !== e.entities || this.cachedDeviceId !== t) && (this.registry = e.entities, this.cachedDeviceId = t, this.entityIds = t === void 0 ? [] : kg({
				hass: e,
				deviceId: t
			})), this.entityIds;
		}
	};
})), U, h_ = t((() => {
	D(), Cg(), U = class extends E {
		static {
			this.properties = { hass: { attribute: !1 } };
		}
		get text() {
			return bg(this.hass?.language ?? "en");
		}
	};
})), W, g_ = t((() => {
	m_(), h_(), W = class extends U {
		constructor(...e) {
			super(...e), this.redraw = new p_();
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
})), __, G, K, q = t((() => {
	D(), __ = {
		primary: "var(--primary-color, #03a9f4)",
		secondary: "var(--secondary-text-color, #727272)",
		disabled: "var(--disabled-text-color, #bdbdbd)",
		warning: "var(--warning-color, #ff9800)",
		error: "var(--error-color, #db4437)",
		success: "var(--success-color, #43a047)"
	}, G = (e) => e === void 0 ? "inherit" : __[e], K = d`
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
})), v_ = /* @__PURE__ */ n({ SajStatusBadge: () => S_ }), y_, b_, x_, S_, C_ = t((() => {
	D(), it(), ut(), R(), B(), P(), Vg(), Wg(), H(), g_(), q(), y_ = "saj-local-status-badge", b_ = `custom:${y_}`, x_ = "operating_mode", S_ = class extends W {
		static {
			this.properties = {
				...W.properties,
				config: { attribute: !1 }
			};
		}
		static {
			this.styles = [K, d`
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
			return I(() => []);
		}
		static getStubConfig(e) {
			return {
				type: b_,
				device: Og(e)[0]?.id
			};
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			return this.config?.device;
		}
		render() {
			let { hass: e, config: t, text: n } = this, r = e === void 0 || t?.device === void 0 ? void 0 : A({
				hass: e,
				deviceId: t.device
			});
			if (e === void 0 || r === void 0 || r.size === 0) return x`<div class="badge dimmed">
                ${n("choose_system")}
            </div>`;
			let i = r.get(x_), a = [i, ...V.map((e) => r.get(e.summaryKey))].filter((e) => e !== void 0), o = !jg(a), s = Bg(r).length, c = o ? i === void 0 ? "" : e.formatEntityState(i.state) : n("not_answering"), l = x`<saj-icon name="inverter"></saj-icon>
            <span
                class="state"
                style=${O({ color: G(Ug(i?.state.state)) })}
                >${c}</span
            >
            ${o && s > 0 ? x`<span
                          class="faults"
                          style=${O({ color: G("error") })}
                          >${n("faults_count", { count: s })}</span
                      >` : w}`;
			return i === void 0 ? x`<div class="badge">${l}</div>` : x`<button
                  type="button"
                  class=${o ? "badge" : "badge dimmed"}
                  @click=${() => {
				ct({
					host: this,
					entityId: i.entityId
				});
			}}
              >
                  ${l}
              </button>`;
		}
	}, customElements.define(y_, S_), Fg({
		type: y_,
		nameKey: "badge_name",
		descriptionKey: "badge_description"
	});
})), w_, T_, E_, D_, O_, k_, A_, j_, M_, N_ = t((() => {
	P(), w_ = .8, T_ = 1e4, E_ = {
		state: "idle",
		line: "none"
	}, D_ = {
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
	}, O_ = ({ kind: e, watts: t }) => {
		if (Math.abs(t) <= 10) return E_;
		let n = D_[e];
		return t > 0 ? n.positive : n.negative;
	}, k_ = (e) => {
		let t = Math.log10(10), n = Math.log10(T_), r = (Math.log10(Math.max(Math.abs(e), 10)) - t) / (n - t);
		return Math.max(w_, 6 - 5.2 * Math.min(r, 1));
	}, A_ = /* @__PURE__ */ new Map([
		["W", 1],
		["kW", 1e3],
		["MW", 1e6]
	]), j_ = (e) => {
		let t = M(e);
		if (t === null) return null;
		let n = e.state.attributes.unit_of_measurement;
		return t * ((typeof n == "string" ? A_.get(n) : 1) ?? 1);
	}, M_ = {
		charging: "charging",
		discharging: "discharging",
		importing: "importing",
		exporting: "exporting",
		idle: "idle"
	};
})), P_, F_, I_, L_, R_, z_, B_, V_ = t((() => {
	D(), q(), P_ = 360, F_ = -90, I_ = 100, L_ = (e) => Math.min(Math.max(e, 0), I_), R_ = (e) => {
		let t = (F_ + L_(e) / I_ * P_) * Math.PI / (P_ / 2), n = (e) => ({
			x: 50 + e * Math.cos(t),
			y: 50 + e * Math.sin(t)
		}), r = n(35), i = n(49);
		return {
			x1: r.x,
			y1: r.y,
			x2: i.x,
			y2: i.y
		};
	}, z_ = (e) => 2 * Math.PI * 42 * L_(e) / I_, B_ = class extends E {
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
			this.styles = [K, d`
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
                stroke=${G(this.tone)}
                stroke-dasharray="${z_(this.percent)} ${e}"
                transform="rotate(-90 ${50} ${50})"
            ></circle>
            ${this.markers.map((e) => {
				let t = R_(e.percent);
				return S`<line class="marker" x1=${t.x1} y1=${t.y1} x2=${t.x2} y2=${t.y2}><title>${e.label}</title></line>`;
			})}
            <text class="centre-value" x=${50} y=${52} text-anchor="middle">${this.displayValue}</text>
            <text class="centre-caption" x=${50} y=${64} text-anchor="middle">${this.caption}</text>`}
        </svg>`;
		}
	}, customElements.define("saj-ring-gauge", B_);
})), H_, U_ = t((() => {
	D(), q(), H_ = class extends E {
		static {
			this.properties = { heading: { type: String } };
		}
		static {
			this.styles = [K, d`
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
	}, customElements.define("saj-card", H_);
})), W_, G_ = t((() => {
	D(), ut(), H(), h_(), q(), W_ = class extends U {
		static {
			this.properties = {
				...U.properties,
				locked: { type: Boolean },
				kind: { type: String },
				deviceId: { type: String },
				message: { type: String }
			};
		}
		static {
			this.styles = [K, d`
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
				path: ot
			})}
              </div>` : x`<div class="empty">
                  <span class="title">${e("empty_title")}</span>
                  <span class="body"
                      >${this.message === "" ? e("empty_enable", { kind: this.kind }) : this.message}</span
                  >
                  ${this.deviceId === void 0 ? w : this.renderLink({
				label: e("open_device_page"),
				path: st(this.deviceId)
			})}
              </div>`;
		}
		renderLink({ label: e, path: t }) {
			return x`<button
            type="button"
            @click=${() => {
				lt({
					host: this,
					path: t
				});
			}}
        >
            ${e}
        </button>`;
		}
	}, customElements.define("saj-empty-state", W_);
})), K_, q_, J_ = t((() => {
	D(), H(), q(), K_ = {
		primary: "info",
		warning: "info",
		error: "fault"
	}, q_ = class extends E {
		static {
			this.properties = {
				message: { type: String },
				tone: { type: String }
			};
		}
		static {
			this.styles = [K, d`
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
                .name=${K_[this.tone]}
                style="color: ${G(this.tone)}"
            ></saj-icon>
            <span class="message">${this.message}</span>
            <slot></slot>
        </div>`;
		}
	}, customElements.define("saj-notice", q_);
})), Y_, X_ = t((() => {
	D(), it(), ut(), H(), q(), Y_ = class extends E {
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
			this.styles = [K, d`
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
                style=${O({ color: G(this.tone) })}
                >${this.value}</span
            >`, t = this.dimmed ? "row dimmed" : "row", { entityId: n } = this;
			return n === void 0 ? x`<div class=${t}>${e}</div>` : x`<button
                  type="button"
                  class=${t}
                  @click=${() => {
				ct({
					host: this,
					entityId: n
				});
			}}
              >
                  ${e}
              </button>`;
		}
	}, customElements.define("saj-value-row", Y_);
})), Z_, Q_, $_, ev, tv, nv, rv, iv, av, ov, sv, J = t((() => {
	P(), Z_ = 1500, Q_ = (e) => {
		let t = e.get("control_allowed") ?? null;
		return {
			locked: t?.state.state === "off",
			entity: t
		};
	}, $_ = (e) => ({
		domain: "number",
		service: "set_value",
		data: { value: e }
	}), ev = (e) => ({
		domain: "select",
		service: "select_option",
		data: { option: e }
	}), tv = (e) => ({
		domain: "time",
		service: "set_value",
		data: { time: e }
	}), nv = (e) => ({
		domain: "switch",
		service: e ? "turn_on" : "turn_off"
	}), rv = () => ({
		domain: "button",
		service: "press"
	}), iv = (e) => `component.${wg}.exceptions.${e}.message`, av = async ({ hass: e, error: t }) => {
		let n = t ?? {}, r = n.message ?? String(t);
		if (n.translation_domain !== "saj_local" || n.translation_key === void 0) return r;
		let i = (await e.loadBackendTranslation("exceptions", wg))(iv(n.translation_key), n.translation_placeholders);
		return i === "" ? r : i;
	}, ov = class {
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
					this.errors.set(e, await av({
						hass: n,
						error: t
					}));
				} finally {
					this.busyEntities.delete(e), this.host.requestUpdate();
				}
			}
		}
	}, sv = class {
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
})), cv, lv, uv, dv, fv, pv = t((() => {
	P(), cv = " ", lv = " - ", uv = (e) => [e.name_by_user ?? e.name ?? "", e.model ?? ""].filter((e) => e !== "").join(cv), dv = (e) => {
		let t = Og(e).map((e) => ({
			device: e,
			base: uv(e)
		}));
		return new Map(t.map(({ device: e, base: n }) => {
			let r = t.filter((e) => e.base === n).length > 1, i = e.serial_number ?? "";
			return [e.id, r && i !== "" ? `${n}${lv}${i}` : n];
		}));
	}, fv = ({ hass: e, deviceId: t }) => dv(e).get(t) ?? "";
})), mv, hv, Y, gv, X, Z = t((() => {
	D(), U_(), G_(), J_(), X_(), g_(), P(), J(), pv(), mv = "opacity: 0.5", hv = [{ type: "entity" }], Y = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [n];
	}), gv = ({ name: e, options: t }) => ({
		name: e,
		default: t.map((e) => e.value),
		selector: { select: {
			options: t,
			multiple: !0,
			mode: "list"
		} }
	}), X = class extends W {
		constructor(...e) {
			super(...e), this.hasControls = !1, this.entityKindKey = "entity_kind_reading", this.tracker = new ov(this, () => this.hass);
		}
		static {
			this.properties = {
				...W.properties,
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
			return e.hass.formatEntityName(t.state, hv);
		}
		valueText({ context: e, entity: t, absolute: n = !1 }) {
			if (j(t)) return this.text("unavailable");
			let r = n ? M(t) : null;
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
			return x`<div style=${e.dimmed ? mv : ""}>
            ${t}
        </div>`;
		}
		render() {
			let { hass: e, config: t } = this;
			if (e === void 0 || t === void 0) return w;
			let { device: n } = t, r = n === void 0 ? /* @__PURE__ */ new Map() : A({
				hass: e,
				deviceId: n
			}), i = n === void 0 ? "" : fv({
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
				lock: Q_(n),
				tracker: this.tracker,
				dimmed: jg(r)
			};
			return r.length === 0 ? this.renderEmpty(i) : x`${i.dimmed ? x`<saj-notice
                      tone="warning"
                      .message=${this.text("not_answering")}
                  ></saj-notice>` : w}${this.renderBody(i)}`;
		}
	};
})), _v = /* @__PURE__ */ n({
	BATTERY_CARD_TYPE: () => vv,
	SajLocalBatteryCard: () => Nv
}), vv, yv, bv, xv, Sv, Cv, wv, Tv, Ev, Dv, Ov, kv, Av, jv, Mv, Nv, Pv = t((() => {
	D(), ut(), B(), P(), N_(), V_(), q(), R(), Z(), vv = "saj-local-battery-card", yv = 5, bv = !0, xv = "battery_soc", Sv = "battery_power", Cv = " · ", wv = ["battery_time_to_full", "battery_time_to_empty"], Tv = {
		charging: "battery_time_to_full",
		discharging: "battery_time_to_empty"
	}, Ev = [
		"backup_reserve_soc",
		"battery_charge_soc_limit",
		"battery_discharge_soc_limit_on_grid"
	], Dv = [
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
	], Ov = [
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
	], kv = [{
		key: "fault",
		tone: "error"
	}, {
		key: "warning",
		tone: "warning"
	}], Av = /^battery_pack(\d+)_/, jv = 10, Mv = ({ number: e, field: t }) => `battery_pack${String(e)}_${t}`, Nv = class extends X {
		constructor(...e) {
			super(...e), this.cardRows = yv;
		}
		static {
			this.styles = [K, d`
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
			return I(() => [F({
				name: "show_packs",
				fallback: bv
			})]);
		}
		static getStubConfig(e) {
			return L(e);
		}
		get showPacks() {
			return this.config?.show_packs ?? bv;
		}
		packNumbers(e) {
			let t = /* @__PURE__ */ new Set();
			for (let n of e.keys()) {
				let e = Av.exec(n);
				e?.[1] !== void 0 && t.add(Number.parseInt(e[1], jv));
			}
			return [...t].sort((e, t) => e - t);
		}
		packEntities({ entities: e, number: t }) {
			return Y({
				entities: e,
				keys: [...Ov, ...kv].map(({ key: e }) => Mv({
					number: t,
					field: e
				}))
			});
		}
		shownEntities(e) {
			if (!e.has(xv)) return [];
			let t = [
				xv,
				...Ev,
				Sv,
				...wv,
				...Dv.map(({ key: e }) => e)
			], n = Y({
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
			return x`${Y({
				entities: t,
				keys: [xv]
			}).map((t) => this.renderGauge({
				context: e,
				soc: t
			}))}
        ${Y({
				entities: t,
				keys: [Sv]
			}).map((t) => this.renderPower({
				context: e,
				power: t
			}))}
        ${this.renderEstimate(e)}
        ${Dv.map(({ key: n, icon: r }) => Y({
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
			let n = Ev.flatMap((t) => {
				let n = e.entities.get(t), r = n === void 0 ? null : M(n);
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
				ct({
					host: this,
					entityId: t.entityId
				});
			}}
        >
            <saj-ring-gauge
                .percent=${M(t) ?? 0}
                .displayValue=${i}
                .label=${r}
                .tone=${j(t) ? "disabled" : "primary"}
                .markers=${n}
                style=${e.dimmed ? "opacity: 0.5" : ""}
            ></saj-ring-gauge>
        </button>`;
		}
		renderPower({ context: e, power: t }) {
			let n = j_(t), r = n === null ? void 0 : M_[O_({
				kind: "battery",
				watts: n
			}).state], i = [this.valueText({
				context: e,
				entity: t,
				absolute: !0
			}), ...r === void 0 ? [] : [this.text(r)]].join(Cv);
			return this.valueRow({
				context: e,
				entity: t,
				icon: "battery",
				value: i
			});
		}
		renderEstimate(e) {
			let t = e.entities.get(Sv), n = t === void 0 ? null : j_(t), r = n === null ? void 0 : Tv[O_({
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
                ${this.text("battery_pack", { number: t })}${kv.map(({ key: r, tone: i }) => {
				let a = n.get(Mv({
					number: t,
					field: r
				}));
				return a !== void 0 && N(a) ? x`<saj-icon
                                  name="fault"
                                  role="img"
                                  aria-label=${this.nameOf({
					context: e,
					entity: a
				})}
                                  style="color: ${G(i)}"
                              ></saj-icon>` : w;
			})}
            </h3>
            ${Ov.map(({ key: r, icon: i }) => {
				let a = n.get(Mv({
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
	}, customElements.define(vv, Nv), z({
		type: vv,
		nameKey: "battery_card_name",
		descriptionKey: "battery_card_description",
		preview: !0
	});
})), Fv, Iv, Q, $ = t((() => {
	D(), H(), h_(), q(), Fv = "saj-commit", Iv = [K, d`
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
    `], Q = class extends U {
		static {
			this.properties = {
				...U.properties,
				label: { type: String },
				labelHidden: { type: Boolean },
				disabled: { type: Boolean },
				busy: { type: Boolean },
				error: { type: String }
			};
		}
		static {
			this.styles = Iv;
		}
		constructor() {
			super(), this.label = "", this.labelHidden = !1, this.disabled = !1, this.busy = !1, this.error = "";
		}
		get inactive() {
			return this.disabled || this.busy;
		}
		commit(e) {
			this.dispatchEvent(new CustomEvent(Fv, {
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
})), Lv = /* @__PURE__ */ n({
	FAULTS_CARD_TYPE: () => Rv,
	SajLocalFaultsCard: () => Uv
}), Rv, zv, Bv, Vv, Hv, Uv, Wv = t((() => {
	D(), Cg(), B(), J(), Vg(), $(), R(), Z(), Rv = "saj-local-faults-card", zv = 4, Bv = !0, Vv = "clear_current_fault", Hv = {
		inverter: "inverter",
		battery: "battery",
		ev: "ev_charger"
	}, Uv = class extends X {
		constructor(...e) {
			super(...e), this.cardRows = zv, this.hasControls = !0;
		}
		static {
			this.styles = [...Iv, d`
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
			return I(() => [F({
				name: "show_groups_without_faults",
				fallback: Bv
			})]);
		}
		static getStubConfig(e) {
			return L(e);
		}
		shownEntities(e) {
			return zg(e).map(({ summary: e }) => e);
		}
		renderBody(e) {
			let t = this.config?.show_groups_without_faults ?? Bv, n = zg(e.entities).filter(({ active: e }) => e || t), r = e.entities.has(Vv);
			return x`${r ? this.renderLockedBanner(e) : w}${n.map((t) => this.renderGroup({
				context: e,
				group: t
			}))}`;
		}
		renderGroup({ context: e, group: t }) {
			let n = this.text(Hv[t.id]);
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
			let n = Sg({
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
			let t = e.entities.get(Vv);
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
					request: rv()
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
	}, customElements.define(Rv, Uv), z({
		type: Rv,
		nameKey: "faults_card_name",
		descriptionKey: "faults_card_description",
		preview: !0
	});
})), Gv = /* @__PURE__ */ n({
	POWER_FLOW_CARD_TYPE: () => Kv,
	POWER_FLOW_SCOPES: () => Zv,
	SajLocalPowerFlowCard: () => yy,
	VIEW_HEIGHT: () => 520,
	VIEW_WIDTH: () => 400
}), Kv, qv, Jv, Yv, Xv, Zv, Qv, $v, ey, ty, ny, ry, iy, ay, oy, sy, cy, ly, uy, dy, fy, py, my, hy, gy, _y, vy, yy, by = t((() => {
	D(), ut(), B(), Wg(), N_(), d_(), q(), R(), Z(), Kv = "saj-local-power-flow-card", qv = 6, Jv = !1, Yv = !0, Xv = "system", Zv = ["system", "parallel"], Qv = 104, $v = 84, ey = 12, ty = 24, ny = -38, ry = 8, iy = 22, ay = 35, oy = 16, sy = 16, cy = " · ", ly = 460, uy = {
		x: 200,
		y: 225
	}, dy = {
		x: 200,
		y: 50
	}, fy = [
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
			position: dy
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
	], py = "operating_mode", my = /^pv([1-9]\d*)_power$/, hy = /\D/g, gy = {
		idle: "var(--divider-color, #e0e0e0)",
		producing: "var(--energy-solar-color, #ff9800)",
		consuming: "var(--primary-color, #03a9f4)",
		charging: "var(--energy-battery-in-color, #f06292)",
		discharging: "var(--energy-battery-out-color, #4db6ac)",
		importing: "var(--energy-grid-consumption-color, #488fc2)",
		exporting: "var(--energy-grid-return-color, #8353d1)"
	}, _y = {
		state: "idle",
		line: "none"
	}, vy = (e) => e.key === "Enter" || e.key === " ", yy = class extends X {
		constructor(...e) {
			super(...e), this.cardRows = qv;
		}
		static {
			this.styles = [K, d`
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
			return I((e) => [
				F({
					name: "show_strings",
					fallback: Jv
				}),
				F({
					name: "show_optional_equipment",
					fallback: Yv
				}),
				Mg({
					name: "scope",
					options: Zv.map((t) => ({
						value: t,
						label: e(`option_scope_${t}`)
					})),
					fallback: Xv
				})
			]);
		}
		static getStubConfig(e) {
			return {
				...L(e),
				scope: Xv
			};
		}
		get scope() {
			return this.config?.scope ?? Xv;
		}
		drawnNodes(e) {
			let { scope: t } = this, n = this.config?.show_optional_equipment ?? Yv, r = fy.flatMap((r) => {
				let i = e.get(r.keys[t]);
				return i === void 0 || r.optional && !n ? [] : [{
					spec: r,
					entity: i
				}];
			}), i = r.filter(({ spec: e }) => e.optional).length, a = 0;
			return r.map(({ spec: n, entity: r }) => {
				let o = j_(r), s = n.secondaryKeys?.[t], c = n.position ?? this.optionalPosition({
					index: a++,
					count: i
				});
				return {
					spec: n,
					entity: r,
					secondaryEntity: s === void 0 ? void 0 : e.get(s),
					watts: o,
					position: c,
					flow: n.kind === null || o === null ? _y : O_({
						kind: n.kind,
						watts: o
					})
				};
			});
		}
		optionalPosition({ index: e, count: t }) {
			return {
				x: 400 * (e + 1) / (t + 1),
				y: ly
			};
		}
		stringEntities(e) {
			return this.config?.show_strings ?? Jv ? [...e.values()].filter((e) => my.test(e.key)).sort((e, t) => this.stringNumber(e) - this.stringNumber(t)) : [];
		}
		stringNumber(e) {
			return Number(e.key.replace(hy, ""));
		}
		hasScopedReadings(e) {
			let { scope: t } = this;
			return fy.some(({ keys: n }) => n.system !== n.parallel && e.has(n[t]));
		}
		shownEntities(e) {
			if (this.scope === "parallel" && !this.hasScopedReadings(e)) return [];
			let t = e.get(py);
			return [
				...t === void 0 ? [] : [t],
				...this.drawnNodes(e).map(({ entity: e }) => e),
				...this.stringEntities(e)
			];
		}
		renderBody(e) {
			let t = this.drawnNodes(e.entities), n = e.entities.get(py), r = this.stringEntities(e.entities);
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
            x2=${uy.x}
            y2=${uy.y}
            style=${i ? `--flow-duration: ${String(k_(r))}s; stroke: ${gy[t.state]}` : ""}
        ></line>`;
		}
		renderNode({ node: e, context: t }) {
			let { spec: n, entity: r, flow: i, position: a } = e, o = n.flowWords ? M_[i.state] : void 0, s = [...e.secondaryEntity === void 0 ? [] : [this.valueText({
				context: t,
				entity: e.secondaryEntity
			})], ...o === void 0 || e.watts === null ? [] : [this.text(o)]].join(cy);
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
				position: uy,
				icon: "inverter",
				label: this.text("inverter"),
				value: this.valueText({
					context: t,
					entity: e
				}),
				secondary: "",
				colour: G(Ug(e.state.state))
			});
		}
		renderTarget({ entity: e, position: t, icon: n, label: r, value: i, secondary: a, colour: o }) {
			let { x: s, y: c } = t;
			return this.renderTap({
				entity: e,
				label: `${r} ${i} ${a}`.trim(),
				content: S`<rect
                class="box"
                x=${s - Qv / 2}
                y=${c - $v / 2}
                width=${Qv}
                height=${$v}
                rx=${ey}
            ></rect>
            <path
                class="icon"
                d=${u_[n]}
                transform="translate(${s - ty / 2} ${c + ny})"
            ></path>
            <text
                class="value"
                x=${s}
                y=${c + ry}
                text-anchor="middle"
                style=${o === void 0 ? "" : `fill: ${o}`}
            >${i}</text>
            <text class="label" x=${s} y=${c + iy} text-anchor="middle">${r}</text>
            <text class="secondary" x=${s} y=${c + ay} text-anchor="middle">${a}</text>`
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
                x=${dy.x}
                y=${dy.y + $v / 2 + sy + t * oy}
                text-anchor="middle"
            >${r}</text>`
			});
		}
		renderTap({ entity: e, label: t, content: n }) {
			let r = () => {
				ct({
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
				vy(e) && (e.preventDefault(), r());
			}}
        >${n}</g>`;
		}
	}, customElements.define(Kv, yy), z({
		type: Kv,
		nameKey: "power_flow_card_name",
		descriptionKey: "power_flow_card_description",
		preview: !0
	});
})), xy = /* @__PURE__ */ n({
	STATUS_CARD_TYPE: () => Sy,
	SajLocalStatusCard: () => jy
}), Sy, Cy, wy, Ty, Ey, Dy, Oy, ky, Ay, jy, My = t((() => {
	D(), B(), P(), Vg(), Wg(), q(), R(), Z(), Sy = "saj-local-status-card", Cy = 5, wy = !0, Ty = [
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
	], Ey = [
		"pv_energy_today",
		"load_energy_today",
		"grid_import_energy_today",
		"grid_export_energy_today",
		"battery_charge_energy_today",
		"battery_discharge_energy_today"
	], Dy = "operating_mode", Oy = "application_mode", ky = "application_mode_active", Ay = "control_allowed", jy = class extends X {
		constructor(...e) {
			super(...e), this.cardRows = Cy;
		}
		static {
			this.styles = [K, d`
            .section {
                padding: 4px 0;
            }
            .section + .section {
                border-top: 1px solid var(--divider-color, #e0e0e0);
            }
        `];
		}
		static getConfigForm() {
			return I(() => [F({
				name: "show_energy",
				fallback: wy
			})]);
		}
		static getStubConfig(e) {
			return L(e);
		}
		get showEnergy() {
			return this.config?.show_energy ?? wy;
		}
		shownEntities(e) {
			return Y({
				entities: e,
				keys: [
					Dy,
					Oy,
					ky,
					...Ty.map(({ key: e }) => e),
					...this.showEnergy ? Ey : [],
					...V.map(({ summaryKey: e }) => e),
					Ay
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
			let t = e.entities.get(Dy);
			return t === void 0 ? [] : [this.valueRow({
				context: e,
				entity: t,
				icon: "inverter",
				tone: Ug(t.state.state)
			})];
		}
		renderMode(e) {
			let t = e.entities.get(Oy);
			if (t === void 0) return [];
			let n = e.entities.get(ky);
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
			return Ty.flatMap(({ key: t, icon: n }) => {
				let r = e.entities.get(t);
				return r === void 0 ? [] : [this.valueRow({
					context: e,
					entity: r,
					icon: n
				})];
			});
		}
		renderToday(e) {
			return Y({
				entities: e.entities,
				keys: Ey
			}).map((t) => this.valueRow({
				context: e,
				entity: t,
				icon: "info"
			}));
		}
		renderFaults(e) {
			if (Y({
				entities: e.entities,
				keys: V.map(({ summaryKey: e }) => e)
			}).length === 0) return [];
			let t = Bg(e.entities), [n] = t, r = t.length;
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
			let t = e.entities.get(Ay);
			if (t === void 0) return [];
			let n = N(t);
			return [this.valueRow({
				context: e,
				entity: t,
				icon: "lock",
				label: this.text("changes"),
				tone: n ? "success" : "warning",
				value: j(t) ? this.text("unavailable") : this.text(n ? "changes_allowed" : "changes_off")
			})];
		}
	}, customElements.define(Sy, jy), z({
		type: Sy,
		nameKey: "status_card_name",
		descriptionKey: "status_card_description",
		preview: !0
	});
})), Ny, Py = t((() => {
	Ke(), Ny = (e) => e ?? w;
})), Fy = t((() => {
	Py();
})), Iy, Ly, Ry = t((() => {
	D(), Fy(), $(), Iy = ({ mode: e, range: t }) => {
		if (e !== "auto") return e;
		let { min: n, max: r, step: i } = t;
		return n === void 0 || r === void 0 || i === void 0 ? "box" : (r - n) / i <= 256 ? "slider" : "box";
	}, Ly = class extends Q {
		static {
			this.properties = {
				...Q.properties,
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
			let e = Iy({
				mode: this.mode,
				range: {
					min: this.min,
					max: this.max,
					step: this.step
				}
			}) === "slider";
			return this.renderFrame(x`<input
                    type=${e ? "range" : "number"}
                    min=${Ny(this.min)}
                    max=${Ny(this.max)}
                    step=${Ny(this.step)}
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
	}, customElements.define("saj-number-control", Ly);
})), zy, By = t((() => {
	D(), $(), zy = class extends Q {
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
	}, customElements.define("saj-press-control", zy);
})), Vy, Hy = t((() => {
	D(), $(), Vy = class extends Q {
		static {
			this.properties = {
				...Q.properties,
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
	}, customElements.define("saj-select-control", Vy);
})), Uy, Wy = t((() => {
	D(), $(), Uy = class extends Q {
		static {
			this.properties = {
				...Q.properties,
				checked: { type: Boolean }
			};
		}
		static {
			this.styles = [...Iv, d`
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
	}, customElements.define("saj-switch", Uy);
})), Gy, Ky, qy = t((() => {
	D(), $(), Gy = 5, Ky = class extends Q {
		static {
			this.properties = {
				...Q.properties,
				value: { type: String },
				draft: { state: !0 }
			};
		}
		constructor() {
			super(), this.onChange = (e) => {
				this.draft = e.target.value;
			}, this.onKeyDown = (e) => {
				e.key === "Enter" && this.finish();
			}, this.onBlur = () => {
				this.finish();
			}, this.value = "", this.draft = null;
		}
		disconnectedCallback() {
			super.disconnectedCallback(), this.finish();
		}
		get shownText() {
			return this.value.slice(0, Gy);
		}
		willUpdate(e) {
			this.disabled && this.draft !== null && (this.draft = null), super.willUpdate(e);
		}
		render() {
			return this.renderFrame(x`<input
                type="time"
                aria-label=${this.label}
                .value=${this.draft ?? this.shownText}
                ?disabled=${this.inactive}
                @change=${this.onChange}
                @keydown=${this.onKeyDown}
                @blur=${this.onBlur}
            />`);
		}
		finish() {
			let e = this.draft;
			this.draft = null, e !== null && e !== "" && e !== this.shownText && this.commit(e);
		}
	}, customElements.define("saj-time-control", Ky);
})), Jy, Yy, Xy, Zy = t((() => {
	D(), J(), P(), Ry(), By(), Hy(), Wy(), qy(), X_(), Jy = [{ type: "entity" }], Yy = ({ hass: e, entity: t }) => e.formatEntityName(t.state, Jy), Xy = ({ context: e, entity: t, labelHidden: n = !1 }) => {
		let { hass: r, lock: i, tracker: a } = e, { attributes: o } = t.state, s = Yy({
			hass: r,
			entity: t
		}), c = i.locked || j(t), l = a.isBusy(t.entityId), u = a.errorOf(t.entityId) ?? "", d = (e) => {
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
                .value=${M(t) ?? 0}
                .min=${o.min}
                .max=${o.max}
                .step=${o.step}
                .unit=${o.unit_of_measurement ?? ""}
                .mode=${o.mode ?? "auto"}
                .displayValue=${r.formatEntityState(t.state)}
                @saj-commit=${(e) => {
				d($_(e.detail));
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
				d(ev(e.detail));
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
				d(nv(e.detail));
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
				d(tv(e.detail));
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
				d(rv());
			}}
            ></saj-press-control>`;
			default: return x`<saj-value-row
                .label=${s}
                .value=${r.formatEntityState(t.state)}
                .entityId=${t.entityId}
            ></saj-value-row>`;
		}
	};
})), Qy = /* @__PURE__ */ n({
	CONTROLS_CARD_TAG: () => $y,
	SECTION_IDS: () => eb,
	SajControlsCard: () => sb
}), $y, eb, tb, nb, rb, ib, ab, ob, sb, cb = t((() => {
	D(), B(), P(), Z(), q(), R(), Zy(), $y = "saj-local-controls-card", eb = [
		"mode",
		"battery",
		"grid",
		"power_control",
		"ev_charger",
		"device"
	], tb = {
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
	}, nb = [
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
	], rb = ({ entities: e, keys: t }) => t.flatMap((t) => {
		let n = e.get(t);
		return n === void 0 ? [] : [{
			kind: "entity",
			entity: n
		}];
	}), ib = (e) => nb.flatMap((t) => {
		let n = e.get(`${t.id}_power_control`), r = e.get(`${t.id}_power_target`);
		return n === void 0 && r === void 0 ? [] : [{
			kind: "power",
			power: t,
			control: n,
			target: r
		}];
	}), ab = ({ entities: e, sections: t }) => eb.filter((e) => t.includes(e)).map((t) => ({
		id: t,
		rows: t === "power_control" ? ib(e) : rb({
			entities: e,
			keys: tb[t]
		})
	})).filter((e) => e.rows.length > 0), ob = (e) => e.kind === "entity" ? [e.entity] : [e.control, e.target].filter((e) => e !== void 0), sb = class extends X {
		constructor(...e) {
			super(...e), this.hasControls = !0, this.entityKindKey = "entity_kind_configuration";
		}
		static {
			this.styles = [K, d`
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
			return I((e) => [gv({
				name: "sections",
				options: eb.map((t) => ({
					value: t,
					label: e(`section_${t}`)
				}))
			})]);
		}
		static getStubConfig(e) {
			return {
				...L(e),
				sections: [...eb]
			};
		}
		get cardRows() {
			let { hass: e, config: t } = this;
			return e === void 0 || t?.device === void 0 ? 1 : ab({
				entities: A({
					hass: e,
					deviceId: t.device
				}),
				sections: this.sections
			}).reduce((e, t) => e + 1 + t.rows.length, 1);
		}
		shownEntities(e) {
			return ab({
				entities: e,
				sections: this.sections
			}).flatMap((e) => e.rows.flatMap(ob));
		}
		renderBody(e) {
			let t = ab({
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
			return this.config?.sections ?? eb;
		}
		renderSection({ context: e, section: t }) {
			return x`<h3>${this.text(`section_${t.id}`)}</h3>
            ${t.rows.map((t) => this.renderRow({
				context: e,
				row: t
			}))}`;
		}
		renderRow({ context: e, row: t }) {
			if (t.kind === "entity") return Xy({
				context: e,
				entity: t.entity
			});
			let n = (t) => t === void 0 ? w : Xy({
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
	}, customElements.define($y, sb), z({
		type: $y,
		nameKey: "controls_card_name",
		descriptionKey: "controls_card_description",
		preview: !0
	});
})), lb, ub, db, fb, pb, mb, hb, gb, _b, vb, yb, bb = t((() => {
	lb = Date.UTC(2024, 0, 1), ub = 864e5, db = {
		monday: 0,
		tuesday: 1,
		wednesday: 2,
		thursday: 3,
		friday: 4,
		saturday: 5,
		sunday: 6
	}, fb = () => Array.from({ length: 7 }, (e, t) => t), pb = (e) => fb().filter((t) => (e >> t) % 2 == 1), mb = (e) => {
		let t = 0;
		for (let n of new Set(e)) t += 2 ** n;
		return t;
	}, hb = ({ value: e, day: t }) => {
		let n = new Set(pb(e));
		return n.has(t) ? n.delete(t) : n.add(t), mb(n);
	}, gb = (e) => {
		let t = new Intl.Locale(e), n = t.getWeekInfo?.() ?? t.weekInfo;
		return n === void 0 ? 0 : n.firstDay - 1;
	}, _b = ({ language: e, locale: t }) => db[t.first_weekday] ?? gb(e), vb = (e) => {
		let t = _b(e);
		return fb().map((e) => (t + e) % 7);
	}, yb = ({ day: e, language: t, width: n }) => new Intl.DateTimeFormat(t, {
		weekday: n,
		timeZone: "UTC"
	}).format(lb + e * ub);
})), xb, Sb, Cb, wb, Tb, Eb, Db, Ob, kb, Ab, jb, Mb, Nb, Pb, Fb, Ib, Lb, Rb, zb, Bb, Vb, Hb, Ub, Wb = t((() => {
	P(), bb(), xb = 1440, Sb = ["time_of_use", "time_of_use_bms"], Cb = "application_mode", wb = 60, Tb = 2, Eb = [
		"charge",
		"discharge",
		"ev_charger"
	], Db = {
		charge: "charge",
		discharge: "discharge",
		ev_charger: "ev"
	}, Ob = [
		"start",
		"end",
		"days",
		"power"
	], kb = [...Ob, "enabled"], Ab = [
		...Ob,
		"mode",
		"grid_charging",
		"battery_discharge"
	], jb = [
		"#307ce8",
		"#f42828",
		"#1a9224",
		"#b76c20",
		"#b153e1",
		"#198c8c",
		"#f21182"
	], Mb = (e) => {
		let t = (e - 1) % jb.length;
		return jb.slice(t, t + 1).join("");
	}, Nb = (e) => e === "ev_charger" ? Ab : kb, Pb = () => Array.from({ length: 7 }, (e, t) => t + 1), Fb = ({ kind: e, number: t }) => `${Db[e]}_slot_${String(t)}`, Ib = ({ entities: e, kind: t, number: n }) => {
		let r = Fb({
			kind: t,
			number: n
		}), i = Nb(t).map((t) => e.get(`${r}_${t}`)), a = i.filter((e) => e !== void 0);
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
	}, Lb = ({ entities: e, kinds: t }) => {
		let n = [], r = 0;
		for (let i of Eb.filter((e) => t.includes(e))) for (let t of Pb()) {
			let a = Ib({
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
	}, Rb = (e) => e.enabled === null || e.enabled.state.state === "on", zb = (e) => {
		let [t, n] = e.state.state.split(":").map(Number);
		return t === void 0 || n === void 0 || !Number.isFinite(t) || !Number.isFinite(n) ? null : t * wb + n;
	}, Bb = (e) => {
		let t = [];
		for (let n of e) {
			let e = zb(n.start), r = zb(n.end), i = M(n.days);
			if (e === null || r === null || i === null) continue;
			let a = !Rb(n), o = (e) => {
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
					endMinute: xb,
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
	}, Vb = ({ day: e, bars: t }) => {
		let n = [...new Set(t.flatMap((e) => [e.startMinute, e.endMinute]))].sort((e, t) => e - t), r = [];
		for (let [i, a] of n.entries()) {
			let o = n[i + 1];
			if (o === void 0) break;
			let s = t.filter((e) => e.startMinute <= a && e.endMinute >= o).map((e) => e.slot).sort((e, t) => e.number - t.number);
			s.length >= Tb && r.push({
				day: e,
				startMinute: a,
				endMinute: o,
				slots: s
			});
		}
		return r;
	}, Hb = (e) => Array.from({ length: 7 }, (e, t) => t).flatMap((t) => Vb({
		day: t,
		bars: e.filter((e) => e.day === t && !e.disabled)
	})), Ub = ({ entities: e, slots: t }) => {
		let n = e.get(Cb);
		return t.some((e) => e.kind !== "ev_charger") && n !== void 0 && !Sb.includes(n.state.state);
	};
})), Gb, Kb = t((() => {
	D(), J(), bb(), $(), Gb = class extends Q {
		static {
			this.properties = {
				...Q.properties,
				value: { type: Number },
				draft: { state: !0 }
			};
		}
		static {
			this.styles = [...Iv, d`
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
			super(), this.delayedCommit = new sv({
				delayMilliseconds: Z_,
				commit: (e) => {
					this.draft = null, this.commit(e);
				}
			}), this.onFocusOut = (e) => {
				e.currentTarget.contains(e.relatedTarget) || this.delayedCommit.flush();
			}, this.value = 0, this.draft = null;
		}
		disconnectedCallback() {
			super.disconnectedCallback(), this.delayedCommit.flush();
		}
		render() {
			let { hass: e } = this;
			if (e === void 0) return x``;
			let { language: t } = e, n = new Set(pb(this.draft ?? this.value)), r = vb(e);
			return this.renderFrame(x`<div
                class="days"
                role="group"
                aria-label=${this.label}
                @focusout=${this.onFocusOut}
            >
                ${r.map((e) => x`<button
                            type="button"
                            aria-pressed=${String(n.has(e))}
                            aria-label=${yb({
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
                                >${yb({
				day: e,
				language: t,
				width: "short"
			})}</span
                            ><span class="narrow"
                                >${yb({
				day: e,
				language: t,
				width: "narrow"
			})}</span
                            >
                        </button>`)}
            </div>`);
		}
		press(e) {
			this.draft = hb({
				value: this.draft ?? this.value,
				day: e
			}), this.delayedCommit.push(this.draft);
		}
	}, customElements.define("saj-weekday-buttons", Gb);
})), qb, Jb, Yb, Xb, Zb, Qb, $b, ex, tx = t((() => {
	D(), it(), J(), P(), Wb(), q(), bb(), H(), Kb(), Zy(), Z(), R(), qb = 4, Jb = !0, Yb = 4, Xb = "-45deg", Zb = (e) => e / xb * 100, Qb = (e) => [...e.filter((e) => e.disabled), ...e.filter((e) => !e.disabled)], $b = (e) => `repeating-linear-gradient(${Xb}, ${e.map((e, t) => `${e} ${String(t * Yb)}px ${String((t + 1) * Yb)}px`).join(", ")})`, ex = class extends X {
		static {
			this.properties = {
				...X.properties,
				expanded: { state: !0 }
			};
		}
		static {
			this.styles = [K, d`
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
                box-sizing: border-box;
                background: none;
                border: 2px solid var(--bar-colour);
            }
            .overlap {
                position: absolute;
                top: 0;
                height: 100%;
                border-radius: 4px;
                cursor: pointer;
            }
            .colour-mark {
                flex: none;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--mark-colour);
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
			return I(() => [F({
				name: "show_timeline",
				fallback: Jb
			})]);
		}
		static getStubConfig(e) {
			return L(e);
		}
		constructor() {
			super(), this.hasControls = !0, this.entityKindKey = "entity_kind_schedule", this.expanded = /* @__PURE__ */ new Set();
		}
		get cardRows() {
			let { hass: e, config: t } = this;
			if (e === void 0 || t?.device === void 0) return 1;
			let { slots: n } = this.scheduleFor(A({
				hass: e,
				deviceId: t.device
			}));
			return 1 + n.length + (this.showTimeline ? qb : 0);
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
				content: x`<h3>${this.text(`option_kind_${this.kind}`)}</h3>
                ${this.renderLockedBanner(e)}${this.renderNotice(e, t)}${this.showTimeline ? this.renderTimeline(e, t) : w}${t.map((t) => this.renderSlot({
					context: e,
					slot: t
				}))}${n === 0 ? w : x`<div class="left-out">
                              ${this.text("slots_left_out", { count: n })}
                          </div>`}`
			});
		}
		scheduleFor(e) {
			return this.scheduled?.entities !== e && (this.scheduled = {
				entities: e,
				schedule: Lb({
					entities: e,
					kinds: [this.kind]
				})
			}), this.scheduled.schedule;
		}
		get showTimeline() {
			return this.config?.show_timeline ?? Jb;
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
			let n = e.entities.get(Cb);
			return n === void 0 || !Ub({
				entities: e.entities,
				slots: t
			}) ? w : x`<saj-notice
            tone="warning"
            .message=${this.text("time_of_use_notice")}
            >${Xy({
				context: e,
				entity: n,
				labelHidden: !0
			})}</saj-notice
        >`;
		}
		renderTimeline(e, t) {
			let n = Bb(t), r = Hb(n), { language: i } = e.hass;
			return x`<div
            class="timeline"
            role="group"
            aria-label=${this.text("week_timeline")}
        >
            ${vb(e.hass).map((e) => x`<div class="day">
                        <span class="day-name"
                            >${yb({
				day: e,
				language: i,
				width: "short"
			})}</span
                        >
                        <div class="track">
                            ${Qb(n.filter((t) => t.day === e)).map((e) => this.renderBar(e))}${r.filter((t) => t.day === e).map((e) => this.renderOverlap(e))}
                        </div>
                    </div>`)}
        </div>`;
		}
		renderBar(e) {
			let { slot: t } = e;
			return x`<button
            type="button"
            class=${e.disabled ? "bar disabled" : "bar"}
            style=${O({
				left: `${String(Zb(e.startMinute))}%`,
				width: `${String(Zb(e.endMinute - e.startMinute))}%`,
				"--bar-colour": Mb(t.number)
			})}
            aria-label=${this.slotName(t)}
            @click=${() => {
				this.expand([t.stem]);
			}}
        ></button>`;
		}
		renderOverlap(e) {
			return x`<div
            class="overlap"
            aria-hidden="true"
            style=${O({
				left: `${String(Zb(e.startMinute))}%`,
				width: `${String(Zb(e.endMinute - e.startMinute))}%`,
				background: $b(e.slots.map((e) => Mb(e.number)))
			})}
            @click=${() => {
				this.expand(e.slots.slice(0, 1).map(({ stem: e }) => e));
			}}
        ></div>`;
		}
		slotName(e) {
			return `${this.text(`option_kind_${e.kind}`)} ${this.text("slot_number", { number: e.number })}`;
		}
		renderSlot({ context: e, slot: t }) {
			let { hass: n } = e, r = this.expanded.has(t.stem), i = M(t.days) ?? 0, a = new Set(pb(i)), o = vb(n).filter((e) => a.has(e)).map((e) => yb({
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
                    <span
                        class="colour-mark"
                        aria-hidden="true"
                        style=${O({ "--mark-colour": Mb(t.number) })}
                    ></span>
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
                ${t.enabled === null ? w : Xy({
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
			let { hass: n, lock: r } = e, i = (t) => t === null ? w : Xy({
				context: e,
				entity: t
			}), { days: a } = t;
			return x`<div class="editor">
            ${i(t.start)}${i(t.end)}${i(t.power)}
            <saj-weekday-buttons
                .hass=${n}
                .label=${this.text("weekdays")}
                .value=${M(a) ?? 0}
                .disabled=${r.locked || j(a)}
                .busy=${this.tracker.isBusy(a.entityId)}
                .error=${this.tracker.errorOf(a.entityId) ?? ""}
                @saj-commit=${(e) => {
				this.tracker.submit({
					entityId: a.entityId,
					request: $_(e.detail)
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
			this.expanded = /* @__PURE__ */ new Set([...this.expanded, ...e]);
		}
	};
})), nx = /* @__PURE__ */ n({
	CHARGE_SCHEDULE_CARD_TAG: () => rx,
	SajChargeScheduleCard: () => ix
}), rx, ix, ax = t((() => {
	B(), tx(), rx = "saj-local-charge-schedule-card", ix = class extends ex {
		constructor(...e) {
			super(...e), this.kind = "charge";
		}
	}, customElements.define(rx, ix), z({
		type: rx,
		nameKey: "charge_schedule_card_name",
		descriptionKey: "charge_schedule_card_description",
		preview: !0
	});
})), ox = /* @__PURE__ */ n({
	DISCHARGE_SCHEDULE_CARD_TAG: () => sx,
	SajDischargeScheduleCard: () => cx
}), sx, cx, lx = t((() => {
	B(), tx(), sx = "saj-local-discharge-schedule-card", cx = class extends ex {
		constructor(...e) {
			super(...e), this.kind = "discharge";
		}
	}, customElements.define(sx, cx), z({
		type: sx,
		nameKey: "discharge_schedule_card_name",
		descriptionKey: "discharge_schedule_card_description",
		preview: !0
	});
})), ux = /* @__PURE__ */ n({
	EV_CHARGER_SCHEDULE_CARD_TAG: () => dx,
	SajEvChargerScheduleCard: () => fx
}), dx, fx, px = t((() => {
	B(), tx(), dx = "saj-local-ev-charger-schedule-card", fx = class extends ex {
		constructor(...e) {
			super(...e), this.kind = "ev_charger";
		}
	}, customElements.define(dx, fx), z({
		type: dx,
		nameKey: "ev_charger_schedule_card_name",
		descriptionKey: "ev_charger_schedule_card_description",
		preview: !0
	});
})), mx = /* @__PURE__ */ n({
	SajWeekdaysFeature: () => yx,
	WEEKDAYS_FEATURE_TAG: () => hx,
	supportsWeekdays: () => vx
}), hx, gx, _x, vx, yx, bx = t((() => {
	D(), B(), J(), P(), g_(), Kb(), Zy(), hx = "saj-local-weekdays-feature", gx = "number.", _x = "_days", vx = ({ hass: e, context: t }) => {
		let n = t.entity_id ?? "";
		return n.startsWith(gx) && (Ag({
			hass: e,
			entityId: n
		})?.key.endsWith(_x) ?? !1);
	}, yx = class extends W {
		constructor(...e) {
			super(...e), this.tracker = new ov(this, () => this.hass);
		}
		static {
			this.properties = {
				...W.properties,
				context: { attribute: !1 },
				config: { attribute: !1 }
			};
		}
		static getStubConfig() {
			return { type: `custom:${hx}` };
		}
		setConfig(e) {
			this.config = e;
		}
		watchedDeviceId() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			return e === void 0 || n === void 0 ? void 0 : Ag({
				hass: e,
				entityId: n
			})?.deviceId;
		}
		render() {
			let { hass: e, context: t } = this, n = t?.entity_id;
			if (e === void 0 || n === void 0) return x``;
			let r = Ag({
				hass: e,
				entityId: n
			});
			if (r === null) return x``;
			let i = A({
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
                .label=${Yy({
				hass: e,
				entity: a
			})}
                .labelHidden=${!0}
                .value=${M(a) ?? 0}
                .disabled=${Q_(i).locked || j(a)}
                .busy=${this.tracker.isBusy(n)}
                .error=${this.tracker.errorOf(n) ?? ""}
                @saj-commit=${(e) => {
				this.tracker.submit({
					entityId: n,
					request: $_(e.detail)
				});
			}}
            ></saj-weekday-buttons>
        </div>`;
		}
	}, customElements.define(hx, yx), Pg({
		type: hx,
		nameKey: "weekdays_feature_name",
		isSupported: (e, t) => vx({
			hass: e,
			context: t
		}),
		configurable: !1
	});
}));
//#endregion
//#region src/index.ts
i().then(() => Promise.all([
	Promise.resolve().then(() => (C_(), v_)),
	Promise.resolve().then(() => (Pv(), _v)),
	Promise.resolve().then(() => (Wv(), Lv)),
	Promise.resolve().then(() => (by(), Gv)),
	Promise.resolve().then(() => (My(), xy)),
	Promise.resolve().then(() => (cb(), Qy)),
	Promise.resolve().then(() => (ax(), nx)),
	Promise.resolve().then(() => (lx(), ox)),
	Promise.resolve().then(() => (px(), ux)),
	Promise.resolve().then(() => (bx(), mx))
]));
//#endregion
