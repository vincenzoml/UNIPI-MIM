# Auto-converted: bengio_2019_arxiv_1909.01310

(First-pass conversion; manual cleanup recommended.)

9
1
0
2

p
e
S
3

]
P
A
.
h
t
a
m

[

1
v
0
1
3
1
0
.
9
0
9
1
:
v
i
X
r
a

Stable mixing estimates in the inﬁnite P´eclet number limit

Michele Coti Zelati♯

ABSTRACT. We consider a passive scalar f advected by a strictly monotone shear ﬂow and with a diffu-
sivity parameter ν ≪ 1. We prove an estimate on the homogeneous ˙H −1 norm of f that combines both the
L2 enhanced diffusion effect at a sharp rate proportional to ν 1/3, and the sharp mixing decay proportional
to t−1 of the ˙H −1 norm of f when ν = 0. In particular, the estimate is stable in the inﬁnite P´eclet number
limit, as ν → 0. To the best of our knowledge, this is the ﬁrst result of this kind since the work of Kelvin
in 1887 on the Couette ﬂow.

The two key ingredients in the proof are an adaptation of the hypocoercivity method and the use of a
vector ﬁeld J that commutes with the transport part of the equation. The L2 norm of Jf together with the
L2 norm of f produces a suitable upper bound for the ˙H −1 norm of the solution that gives the extra decay
factor of t−1.

1. Introduction

Questions related to the understanding of the interaction between mixing and diffusion in ﬂuid
mechanics date back to the fundamental works of Kelvin [27] and Reynolds [34]. When considering a
R and diffused, one would like to
R, advected by a shear u : R
passive scalar f : [0,
study in a quantitative way the long-time behavior of solutions to the drift-diffusion equation

→

∞

→

×

×

R

T

)

∂tf + u∂xf = ν∆f,
f (0, x, y) = f in(x, y),

(

T

×

×

R,

in (0,
in T

)
∞
R.
×

(1.1)

Here, ν > 0 is the diffusivity coefﬁcient, proportional to the inverse P´eclet number, and f in is a given
mean-free initial datum. The case of the Couette ﬂow u(y) = y is an enlightening example: the equation
can be solved explicitly using the Fourier transform, giving

f (t, ℓ, η) =

f in(ℓ, η + ℓt) exp

t

ν

−

(cid:26)

0
Z

ℓ2 +

η + ℓt
|

−

ℓτ

2
|

dτ

,

(ℓ, η)

(cid:27)

Z

×

∈

R.

(1.2)

(cid:2)

(cid:3)

c

f in(ℓ, η + ℓt) is due to inviscid mixing. For ℓ

b
The term
= 0, it implies a transfer of information to high
frequencies, producing, even when ν = 0, a decay of solutions proportional to 1/t in the negative H −1
Sobolev norm, namely
c

y

f (t, ℓ)
k

kH

−1
y

:=

Consequently, we ﬁnd

b

2
f (t, ℓ, η)
ℓ2 + η2 dη
|
|
b

≤

R

Z

2

1 + (ℓt)2 k

f in(ℓ)

kH 1

y

,

t

∀

≥

0.

(1.3)

p

c

2
√1 + t2 k
where f6= denotes the projection of f onto non-zero modes in x, i.e. f minus its x-average. Note that
the x-average of the equation is a conserved quantity for (1.1) when ν = 0, so there is no hope of decay

f in
6= k ˙H 1,

f6=(t)
k

k ˙H −1

(1.4)

≥

≤

0,

∀

t

2000 Mathematics Subject Classiﬁcation. 35K15, 35Q35, 76F25, 76R50.
Key words and phrases. Mixing, enhanced diffusion, hypocoercivity, vector ﬁeld, shear ﬂows, drift-diffusion equation.
♯m.coti-zelati@imperial.ac.uk, Department of Mathematics, Imperial College London, London, SW7 2AZ, UK.

1

6

2

M. COTI ZELATI

for the ℓ = 0 mode. On the other hand, for ν > 0, the (super) exponential factor in (1.2) causes a decay
in L2 of the type

In particular, summing over all ℓ

b

1

12 νℓ2t3

f (t, ℓ)
k

e−

η ≤

kL2
= 0, we obtain

f6=(t)
k

kL2

≤

1

12 νt3

e−

f in(ℓ)
k

kL2

η

,

t

∀

≥

0.

c
f in
6= kL2,
k

t

∀

≥

0.

(1.5)

(1.6)

1
We refer to this estimate as enhanced diffusion, as it implies homogenization at a time-scale O(ν−
3 ),
hence much shorter than the diffusive time-scale O(ν−1). Again, the ℓ = 0 mode satisﬁes the one-
dimensional heat equation, so the restrictions to all nonzero modes in x is necessary. The intriguing fact
about the Couette ﬂow is that the two estimates (1.4) and (1.6) can be combined in a single one, in the
sense that one can prove that

f6=(t)
k

k ˙H −1

≤

1
12 νt3

2e−
√1 + t2 k

f in
6= k ˙H 1,

t

∀

≥

0.

(1.7)

The above (1.7) is what we refer to as a stable mixing estimate in the inﬁnite P´eclet number limit, since
there is no harm in setting ν = 0 and still obtaining non-trivial information about f , unlike in (1.6).
Needless to say, having the explicit solution (1.2) at our disposal is crucial in deducing such estimate,
and in fact this is essentially what Kelvin did in [27] back in 1887. To this date, (1.7) remains the only
stable mixing estimate available in the literature.

1.1. The main results. The goal of this paper is to prove stable mixing estimates for (1.1) for a

large class of strictly monotone shear ﬂows. Assume that u

C 3 and that there exists U

1
U ≤

u′(y),

u′′(y)
|
|
u′(y) ≤

U,

∈
u′′′(y)
|
|
u′(y) ≤

U,

R.

y

∀

∈

Let f be the solution to (1.1) or to the hypoelliptic drift-diffusion equation

∂tf + u∂xf = ν∂yyf,
f (0, x, y) = f in(x, y),

(

T

×

×

R,

in (0,
in T

)
∞
R.
×

Consider the L2-weighted norm deﬁned by

1 such that

≥

(H)

(1.8)

2
L2.
k
Throughout the article, the initial datum f in is required to satisfy
detailed study of the longtime dynamics of (1.8), including a stable mixing estimate resembling (1.7).

f in
6= ku′ <
k

. Our main result is a

2
u′ :=
k

2
L2 +
k

u′f
k

(1.9)

f
k

f
k

∞

THEOREM 1.1. There exist C0 ≥
we have the enhanced diffusion estimate

1 and ε0, ν0 ∈

(0, 1) only depending on U such that if ν

f6=(t)
k
and the stable mixing estimate

ku′

≤

C0e−ε0ν1/3t

f in
6= ku′,
k

t

∀

≥

0,

f in
6= ku′ +
k
In particular, if ν = 0 we obtain the inviscid mixing estimate

f6=(t)
k

k ˙H −1

C0

≤

(cid:2)

∂yf in
k

6= ku′

e−ε0ν1/3t
√1 + t2

C0
√1 + t2
All the constants can be computed explicitly.

f6=(t)
k

k ˙H −1

≤

f in
6= ku′ +
k

∂yf in
k

6= ku′

(cid:2)

,

t

∀

≥

0.

t

∀

≥

0.

(cid:3)

,

(cid:3)

[0, ν0]

∈

(1.10)

(1.11)

(1.12)

Before we proceed to explain the main ideas of the proofs and expand on the concepts of mixing

and enhanced diffusion, a few remarks are in order.

6

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

3

REMARK 1.2 (On the class of shear ﬂows). In addition to strict monotonicity, assumption (H) es-
on u and its derivatives. Besides small perturbations

sentially imposes a growth condition at
of the Couette ﬂow, such as

y
|

| → ∞

1
2
it allows up to exponential growth at inﬁnity, including

u(y) = y +

sin y,

u(y) = y + ey,

and

u(y) = y(1 +

y
|

n−1),
|

3 (for n = 2, one has to smooth out at y = 0, but of course quadratic grow at inﬁnity is allowed).

for n
What is not included is highly oscillatory shear ﬂows, such as

≥

u(y) = y +

1
2

y

0

sin(z2)dz,

Z

3
2 , but such that u′′(y) = y cos(y2), violating (H).

for which 1

2 ≤

u′

≤

REMARK 1.3 (On the weighted norm). The choice of the norm (1.9) appears naturally in the proof,
In the particular case u(y) = y2,
and precisely accounts for the possible growth at inﬁnity of u′.
this choice has been made in [16] for proving an enhanced dissipation estimate of the type (1.10) for
the vorticity in the Navier-Stokes equations near the Poiseuille ﬂow. Usually, this choice implies a
logarithmic loss in the decay rate (1.10), while in our case, due to strict monotonicity, this loss can be
avoided. Notice that if u′ is assumed to be bounded, the norm simply reduces to the standard L2 norm.

REMARK 1.4 (On the super exponential decay). The enhanced diffusion estimate (1.10) is a semi-
group estimate for the linear operator appearing in (1.8). Whether a super-exponential decay of the type
present in (1.6) or (1.7) holds for ﬂows different than the Couette ﬂow is an open question, and it is re-
lated to the spectral properties of the linear operator L = iku(y)
ν∂yy. In particular, when u(y) = y,
the operator L has empty spectrum, which is a necessary condition for a semigroup to decay faster than
exponentially.

−

REMARK 1.5 (Hypoellipticity). All the estimates of Theorem 1.1 can be made more precise by
stating them for each x-Fourier mode, similarly to (1.3) and (1.5). In particular, it can be proven that for
each ℓ

= 0 there holds

f (t, ℓ)
k

ku′

≤

C0e−ε0ν1/3|ℓ|2/3t

f in(ℓ)
k

ku′,

for every t
since it provides a quantiﬁcation of the instantaneous regularization from L2 to Gevrey- 3
diffusion in x is present in the equation. For a precise statement, see Theorem 4.1 below.

0. As noted in [6], this estimate is particularly relevant for the hypoelliptic equation (1.8),
2 even if no

c

≥

b

REMARK 1.6 (The Batchelor scale). The characteristic ﬁlamentation length scale of f can be deﬁned

in terms of the ratio

f (t)
λ(t) = k
f (t)
k

k ˙H −1
kL2

.

In many situations it is expected (see [33] and references therein) that λ(t)
→ ∞
(possibly in a time-averaged sense) and whenever ν > 0. Our result is not in contrast with this prediction,
as it is conceivable to think that the constant ε0 appearing in (1.10) is in fact bigger than that appearing
in (1.11). Moreover, we only provide upper bounds, which do not say much about the behavior of λ(t).
However, it is worth keeping in mind that the exponent 1/3 is optimal, and that when ν = 0 the result
implies that λ(t)

cν > 0, as t

0 as t

= 0.

→

→

whenever f in
6= 6

→ ∞

1.2. Mixing and enhanced diffusion. One of the main effects of transport is the generation of an
averaging effect that creates smaller and smaller spatial scales as time increases. Thinking on the Fourier
side, this is equivalent to the accumulation of energy in higher and higher Fourier modes, as precisely
f in(ℓ, η + ℓt) in (1.2) in the speciﬁc example of the Couette ﬂow. It is therefore
described by the term
not surprising that a way to quantify this is through the decay of a negative Sobolev norm, as in (1.12).
In the context of passive scalars, this point of view was introduced in [31], and it is deeply connected
with the regularity of transport equations [12, 18, 26, 45], the quantiﬁcation and lower bounds on mixing

c

6

4

M. COTI ZELATI

rates [1, 6, 19, 25, 32, 36, 46], and the inviscid damping in the two-dimensional Euler equations linearized
around shear ﬂows [8, 17, 23, 40, 42, 43, 47–49].

On the other hand, once a passive scalar is well concentrated at high frequencies, diffusion becomes
the dominant effect. Understanding at which ν-dependent time-scale this happens is fundamental in
order to capture correctly the dynamics. An enhanced diffusion estimate of the type (1.10) precisely
tells us that on a short time-scale O(ν−1/3), the solution becomes x-independent, while its x-average
remains order 1 until the diffusive time-scale O(ν−1). This separation of time-scales has been the object
of study in a vast part of the ﬂuid mechanics literature [2, 21, 28, 35]. The rigorous mathematical study
has been initiated in [13], and has become of great interest in the last years [3–7, 9–11, 13, 14, 20, 22, 24,
29, 30, 39, 40].

1.3. Main ideas. The proof of the enhanced diffusion estimate (1.10) is based on a modiﬁcation of
the so-called hypocoercivity method [38]. In the context of ﬂuid mechanics, it was successfully used for
the ﬁrst time in [3] to study the Kolmogorov ﬂow u(y) = sin y, and then for general shear ﬂows in [6]
on a periodic domain or a bounded periodic channel. Other examples include circular ﬂows [15], the 2D
Navier-Stokes equations [16, 41] and the Boussinesq equations [37]. Although the proof is very simple
R is not present in the literature, and we
due to strict monotonicity, a proof in the spatial domain T
decided to include it here to make the paper self-contained.

×

Estimate (1.11) is the real novelty of this article. It relies on the observation that the vector ﬁeld
J = ∂y + tu′∂x
commutes with the transport part of (1.8). Hence, the idea is to apply the hypocoercivity method not
only to f , but also to Jf . In view of the fact that the commutator [J, ∂yy]
= 0, the scheme is much
more involved and has to be carried out simultaneously for f and Jf . Once a proper enhanced diffusion
estimate of the type (1.10) is proven for both f and Jf , one simply uses the fact that (see Lemma 3.2)

(1.13)

The above inequality holds thanks to the monotonicity assumption in (H). The vector ﬁeld (1.13) was
used in the context of inviscid damping for the for the 2D β-plane equation [44].

t

f
k

k ˙H −1 .

f
k

kL2 +

Jf
k

kL2.

1.4. Notation and conventions. All the proofs are carried out for the harder case of the hypoelliptic
denote the standard L2 norm and scalar product

equation (1.8). Throughout the paper,
respectively. Via an expansion of f as a Fourier series in the x variable, namely

k · k

,
h·

and

·i

f (t, x, y) =

f (t, ℓ, y)eiℓx,

f (t, ℓ, y) =

Xℓ∈Z

b

b

1
2π

T
Z

f (t, x, y)e−ikxdx,

for k

∈

N0 we set

This way we may express

fk(t, x, y) :=

f (t, ℓ, y)eiℓx.

(1.14)

X|ℓ|=k

b

f (t, x, y) =

fk(t, x, y)

as a sum of real-valued functions fk that are localized in x-frequency on a single band
∈
thus see that (1.8) decouples in k and becomes an inﬁnite system of one-dimensional equations.

k, k

±

Xk∈N0

N0. We

Given two operators A, B, the symbol [A, B] = AB

BA denotes the commutator between the

two. Unless otherwise stated, all the constants will be independent of ν and k, but may depend on U.

−

2. Hypocoercivity for the passive scalar

In this section, we tackle the question of enhanced diffusion for f . This is carried out by the so-called

hypocoercivity method and the construction of a suitable energy functional. Let

α = α0

ν2/3
k2/3 ,

β = β0

ν1/3
k4/3 ,

γ = γ0

1
k2 .

(2.1)

6

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

where

For each k

∈

α0 =

4

1
3504U6 , ,

β0 = 4α2
0,

γ0 = 128α3
0.

×

N, deﬁne the functional
1
2

fkk
k

Φk =

2 + α
∂yfkk
k

2 + 2β

u′∂xfk, ∂yfki
h

+ γ

u′∂xfkk
k

2

,

5

(2.2)

(2.3)

where fk is given by (1.14). It is important to notice that the choice (2.1) and (2.2) implies that Φk is
coercive. Indeed, since

(cid:3)

(cid:2)

2β

u′∂xfk, ∂yfki| ≤
|h

2β

u′∂xfkkk
k

∂yfkk ≤

and, in particular,

we ﬁnd that

β2
αγ ≤

1
4

,

α
2 k

2 +

∂yfkk

2β2
α k

2,
u′∂xfkk

1
4

2 + α
∂yf
k
k

f
2
k

Φk ≤
Then main result of this section is the derivation of a suitable differential inequality for Φk, contained in
(cid:2)
the proposition below.

f
2
k

2 + 3α
∂yf
k
k

2 + 3γ
k

u′∂xf
k

u′∂xf
k

2 + γ
k

(2.4)

2
k

2
k

≤

(cid:2)

(cid:3)

(cid:3)

.

1
4

PROPOSITION 2.1. Assume that νk−1
ν
4 k

Φk + 2ε0ν1/3k2/3Φk +

d
dt

≤
∂yfkk

2 +

≥
∂yyfkk

να
2 k

2 +

1. For every t

0, there holds

where

and β0 is given in (2.2).

ε0 :=

β0
32U2

νγ
2 k

u′∂xyfkk

2

0,

≤

(2.5)

(2.6)

As we shall see in a moment, the choice of the coefﬁcients (2.2) and (2.6) is an overkill in the proof
of Proposition 2.1, but will be necessary for Proposition 3.1. Since we do not want to make two different
choices in the parameters, we opted for a uniﬁed selection.

2.1. Energy balances. We begin by computing the time derivative of Φk. At this stage, we omit
in the estimates.

the subscript in all the functions, keeping in mind the useful relation
Relying on the antisymmetry of the transport term, we test (1.8) by f and derive the energy balance

∂xf
k

f
k

= k

k

k

d
f
dt k
Regarding the L2 balance for ∂yf , we obtain

1
2

2 + ν
k

∂yf
k

2 = 0.
k

(2.7)

2 =
k
where the right-hand side above appears because of the commutator relation [∂y, u∂x] = u′∂x. Turning
to the β-term in (2.3), we have

u′∂xf, ∂yf

2 + ν
k

∂yyf
k

(2.8)

∂yf

−h

,
i

1
2

d
dt k

d
dt h

i

= ν

u′∂xf, ∂yf

u′∂xf, ∂y(u∂xf )
i
i
u′′∂xf, ∂yyf
(cid:3)
(2.9)
h
where we integrated by parts, used the antisymmetry of u′′∂x and the crucial relation [u∂x, u′∂x] = 0.
Finally, the time derivative of the γ-term in (2.3) can be computed as

u′∂xyyf, ∂yf
h
(cid:2)
2ν
−

i
u′∂xyf, ∂yyf
h

u′∂xf, ∂yyyf
h

u′∂x(u∂xf ), ∂yf

u′∂xf

2,
k

i − k

i − h

− h

i −

=

+

ν

1
2

d
dt k

u′∂xf

2 = ν
k

u′∂x, u′∂xyyf
h
ν

u′∂xyf
k
u′∂xyf
k

−

−

ν

i − h
2
2ν
k
−
2 + ν
k

=

=

u′∂x, u′∂x(u∂xf )
i

u′u′′∂xf, ∂xyf
h
i
(u′u′′)′∂xf, ∂xf
h

.
i

6

Therefore,

M. COTI ZELATI

1
2

d
dt k

u′∂xf

2 + ν
k

u′∂xyf
k

2 = ν
k

(u′u′′)′∂xf, ∂xf
h

.
i

Collecting (2.7), (2.8), (2.9) and (2.10) we obtain

d
dt

Φ + ν

∂yf
k

2 + β
2 + να
∂yyf
k
k
k
u′∂xyf, ∂yyf
2νβ
h

i −

u′∂xf
k
νβ

u′∂xyf
2 + νγ
k
k
u′′∂xf, ∂yyf
h

+ νγ

u′∂xf, ∂yf
α
h

2 =
k
−
(u′u′′)′∂xf, ∂xf
h

.
i

i

−

We now proceed in estimating the error terms above, one by one.

(2.10)

i

(2.11)

2.2. Error estimates and proof of Proposition 2.1. In what follows, we will repeatedly use the
Cauchy-Schwarz and Young inequalities without mention. We begin from the α-term in the right-hand
side of (2.11). We have

u′∂xf, ∂yf

α

|h

u′∂xf
α
k

∂yf

kk

k ≤

i| ≤

ν
2 k

∂yf

2 +
k

α2
2ν k

u′∂xf

2.
k

Since by (2.1)-(2.2) we have

we ﬁnd

α2
βν ≤

1
2

,

ν
2 k

∂yf

2 +
k

β
4 k

u′∂xf

2.
k

i| ≤

u′∂xf, ∂yf

α

|h

For the ﬁrst of the β-terms in (2.11), we have

2νβ

u′∂xyf, ∂yyf

|h
so that since (2.2) implies that

2νβ

u′∂xyf
k

∂yyf

kk

k ≤

i| ≤

να
4 k

∂yyf

2 +
k

β2
αγ

=

1
8

,

4νβ2

u′∂xyf

2,
k

α k

we obtain

i| ≤
The second β-term can be instead estimated as

|h

2νβ

u′∂xyf, ∂yyf

να
4 k

∂yyf

2 +
k

γν
2 k

u′∂xyf

2.
k

νβ

u′′∂xf, ∂yyf

i| ≤
|h
so that using (2.13) and (H) we have

νβ

u′′∂xf
k

∂yyf

kk

k ≤

να
4 k

∂yyf

2 +
k

νβ2
α k

u′′∂xf

2,
k

νβ

u′′∂xf, ∂yyf

|h

να
4 k

∂yyf

2 + U2 νγ
8 k
k

u′∂xf

2.
k

i| ≤

Lastly, we have

|h
Collecting (2.12), (2.14), (2.15), (2.16) and using (2.11) we arrive at

i| ≤

νγ

(u′u′′)′∂xf, ∂xf

2νU2γ

u′∂xf
k

2.
k

(2.12)

(2.13)

(2.14)

(2.15)

(2.16)

d
dt

Φ +

ν
2 k

∂yf

2 +
k

να
2 k

∂yyf

2 +
k

3β
4 k

u′∂xf

2 +
k

νγ
2 k

u′∂xyf

2
k

3U2νγ

u′∂xf
k

2.
k

(2.17)

Looking at the right-hand side of (2.17), recalling that νk−1

3U2νγ

u′∂xf
k

2 = 3U2 γ0
β0
k

where we used that from (2.2) we have

ν
k

(cid:16)

2/3

β

(cid:17)

≤
1 and using (2.1), we have

≤
u′∂xf
k

2
k

≤

β
4 k

u′∂xf

2,
k

γ0
β0

= 32α0 ≤

1
12U2 .

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

7

Thus, (2.17) becomes

d
dt

Φ +

ν
2 k

∂yf

2 +
k

να
2 k

∂yyf

2 +
k

β
2 k

u′∂xf

2 +
k

νγ
2 k

u′∂xyf

2
k

≤

0.

(2.18)

In view of (2.1) and (H), this implies

d
dt

Φ +

βk2
f
4U2 k

2 +
k

ν
2 k

∂yf

2 +
k

β
4 k

u′∂xf

2 +
k

να
2 k

∂yyf

2 +
k

νγ
2 k

u′∂xyf

2
k

≤

0,

or, equivalently,

d
dt

Φ +

In light of (2.2), we have

Using (2.4) we have

β0
8U2 ν1/3k2/3
ν
∂yf
4 k

+

f
2
k
(cid:20)
2 +
k

2 +
k
να
2 k

2U2
α0β0

∂yf
α
k
2 +
k

νγ
2 k

2U2
2 +
γ0
k
u′∂xyf

∂yyf

2
k

0.

≤

γ

u′∂xf
k

2
k

(cid:21)

2U2
α0β0 ≥

3,

2U2
γ0 ≥

3.

d
dt

Φ +

β0
4U2 ν1/3k2/3Φ +

ν
4 k

∂yf

2 +
k

να
2 k

∂yyf

2 +
k

νγ
2 k

u′∂xyf

2
k

≤

0.

In particular, this implies (2.5), and the proof of Proposition 2.1 is concluded.

3. Hypocoercivity and the vector ﬁeld method

Let us deﬁne the vector ﬁeld

J = ∂y + tu′∂x,

and, for each k

N, the corresponding energy functional

(3.1)

(3.2)

∈
Jk =

(cid:2)

1
2

Jfkk
k

2 + α
∂yJfkk
k

2 + 2β

u′∂xJfk, ∂yJfki
h

+ γ

u′∂xJfkk
k

2

,

where the various coefﬁcients are exactly the same as in (2.1)-(2.2). Thus, in particular, there holds

(cid:3)

1
4

(cid:2)

Jfkk
2
k

2 + α
∂yJfkk
k

2 + γ

u′∂xJfkk
k

2

≤ Jk ≤

1
4

Jfkk
2
k

2 + 3α
∂yJfkk
k

2 + 3γ

(cid:3)

(cid:2)

u′∂xJfkk
k

2

.
(3.3)
(cid:3)

The goal here is to prove a result analogous to Proposition 2.1, but with a slightly more complicated
form.

PROPOSITION 3.1. Assume that νk−1

ν0, where

≤

ν0 :=

3/2

.

β0
7008U8

(cid:19)

4

(cid:18)

×

For every t

0, there holds

≥
d
dt Jk + 2ε0ν1/3k2/3

∂yfkk
k
where ε0 is the same as in (2.6) and β0 is given in (2.2).

Jk ≤

(cid:2)

3504νU6

2 + α
∂yyfkk
k

2 + γ

(3.4)

(3.5)

u′∂xyfkk
k

2

,

(cid:3)

The proof of the above result is vaguely reminiscent of that of Proposition 2.1, and it will be carried

out in the next sections.

8

M. COTI ZELATI

3.1. The vector ﬁeld and inviscid mixing estimates. Before going to the proof, let us clarify the
reason of the choice of the vector ﬁeld in (3.1). We apply J to the advection diffusion equation (1.8).
Since

[J, ∂t + u∂x] = 0

and

we have that

[J, ∂yy] =

tu′′′∂x −

−

2tu′′∂xy =

=

u′′′
u′ (J

−
u′′′
u′ (J

∂y)

−

−

2u′′∂y

1
u′ (J

−

∂y)

(cid:19)

(cid:18)
u′′
u′ (J

∂y)

−

−

2∂y

(cid:18)

−

∂y)

,

(cid:19)

∂tJf + u∂xJf = ν∂yyJf + ν

u′′′
u′ (Jf

−

∂yf )

−

2ν∂y

u′′
u′ (Jf

−

(cid:18)

∂yf )

.

(cid:19)

(3.6)

It is clear from the above computation why the strict monotonicity requirement on u is important. The
crucial property of J is that, combined with the L2 norm of fk, it provides a bound on the ˙H −1 norm of
fk itself, with an extra factor of t. This is essentially contained in [44].

LEMMA 3.2. Let k

∈

N. There there holds

kt

fk(t)
k

k ˙H −1

≤

2U2 [

fk(t)
k
k

+

] ,
Jfk(t)
k
k

(3.7)

for every t > 0.

PROOF OF LEMMA 3.2. For each k

the elliptic problem

∈

N, let us deﬁne the “stream-function” ψk as the solution to

with appropriate periodic boundary conditions in x, decay in y, and mean zero condition. Then, a series
of integration by parts entails

∆ψk = fk,

t

k∇

2 =

∂xψkk

=

≤

Thus

−

t

∂xψk, ∂xfki
h
1
u′ Jfki
∂xψk,
Jfkk
∂xψkkk
k

−h
U

=

=

∂xψk,

1
u′ tu′∂xfki
−h
1
u′ ∂xψk, ∂yfki
+
=
−h
h
+ U
+ U [
]
∂xψkk
∂xyψkk
k
k

1
u′ (Jfk −
∂y(

∂xψk,

−h

1
u′ Jfki − h
∂xψk,
.
fkk
k

∂yfk)
i
1
u′ ∂xψk), fk)
i

t

∂xψkk ≤

k∇

2U2 [

fkk
k

+

] ,
Jfkk
k

which readily implies (3.7) and concludes the proof.

(cid:3)

The power of this technique can be understood by looking at (3.6) for ν = 0. In that case, we ﬁnd

d
dt

2 +

fkk
k

2

Jfkk
k

= 0,

and since Jfk(0) = ∂yf in

k , we ﬁnd from (3.7) that

(cid:2)

(cid:3)

(kt)2

2
fk(t)
˙H −1
k
k

≤

4U4

f in
k k
k

2 +

2
∂yf in
k k
k

.

This implies (1.12), and in fact it does not even require the weighted L2 norm. However, the proof of
(1.11) is much more involved.

(cid:2)

(cid:3)

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

9

3.2. Energy balances. As in Section 2.1, we omit the dependence on k of the various functions.

We begin by testing (3.6) with Jf . We have
u′′′
u′ (Jf

2 = ν
k

2 + ν
k

∂yJf
k

d
dt k

1
2

Jf

h

Thus, integrating by parts the last term entails

(cid:20)

∂yf ), Jf

∂y
2
h

i −

−

u′′
u′ (Jf

−

(cid:18)

∂yf )

, Jf

(cid:19)

i
(cid:21)

where

1
2

d
dt k

Jf

2 + ν
k

∂yJf
k

2 = νE0
k

E0 =

u′′′
u′ (Jf

h

−

∂yf ), Jf

+ 2
h

i

u′′
u′ (Jf

−

∂yf ), ∂yJf

.
i

(3.8)

(3.9)

Taking ∂y of (3.6), we have

∂t∂yJf + u∂xyJf = ν∂yyyJf + ν∂y

(cid:18)
Thus, multiplying by ∂yJf in L2, we have
u′′′
1
∂y
u′ (Jf
2
h
−
u′∂xJf, ∂yJf

∂yyJf
k

2 + ν
k

2 =ν
k

d
dt k

∂yJf

(cid:18)

(cid:20)

u′′′
u′ (Jf

−

∂yf )

(cid:19)

2ν∂yy

−

(cid:18)

u′′
u′ (Jf

−

∂yf )

(cid:19)

u′∂xJf.

−

∂yf )

, ∂yJf

(cid:19)

∂yy
2
h

i −

(cid:18)

u′′
u′ (Jf

−

∂yf )

, ∂yJf

(cid:19)

i
(cid:21)

i
∂yf ), ∂yyJf

− h

ν

=

−

− h

u′′′
u′ (Jf
−
(cid:20)
u′∂xJf, ∂yJf

h

i

∂y
2
h

i −

(cid:18)

u′′
u′ (Jf

−

∂yf )

, ∂yyJf

(cid:19)

i
(cid:21)

As a consequence,

having deﬁned

E1 =ν

(cid:20)

1
2

d
dt k

∂yJf

2 + ν
k

∂yyJf
k

2 = E1,
k

(3.10)

(3.11)

∂yyf ), ∂yyJf

i
(cid:21)

u′u′′′ + 2(u′′)2
(u′)2
h
u′∂xJf, ∂yJf

.
i

− h

(Jf

−

∂yf ), ∂yyJf

u′′
u′ (∂yJf

2
h

−

i −

Turning to the β-term in (3.2), using (3.6) and several integration by parts we have

d
dt h

u′∂xJf, ∂yJf

= ν

+

u′∂xJf
k

2
k
u′∂xJf, ∂yyyJf
h

i

+

i

i
u′∂xyyJf, ∂yJf
h
(cid:20)
+

u′∂x
h

(cid:18)
u′∂xy
2
h

−

−

u′′′
u′ (Jf
u′′
u′ (Jf

(cid:18)

−

= ν

−

(cid:20)

u′∂xyJf, ∂yyJf
2
h

i − h

u′′∂yyf, ∂xyJf
4
h

−

4
h

i −

u′′∂xJf,
+ 2
h

u′′
u′ (∂yJf

−

implying

∂yf )

, ∂yJf

+

i

u′∂xJf, ∂y
h

(cid:19)
∂yf )

, ∂yJf

i −

(cid:19)
u′′∂xJf, ∂yyJf

−

u′′′
u′ (Jf
u′′
u′ (Jf

∂yf )

i
(cid:19)
∂yf )

(cid:18)
u′∂xJf, ∂yy
2
h

(cid:18)
u′′′∂xJf, ∂yJf
2
h

i −

i
(cid:21)
(cid:19)

u′u′′′

(u′′)2

−
u′

∂xJf, ∂yJf

i − h

6u′u′′′

4(u′′)2

∂yf, ∂xyJf

i

∂yyf )

i − h

u′′∂xJf,

u′u′′′

2(u′′)2

−
(u′)2

∂yf

,

i
(cid:21)

−

i

−
u′

d
dt h

u′∂xJf, ∂yJf

+

u′∂xJf
k

2 = νE2,
k

i

(3.12)

10

M. COTI ZELATI

for E2 deﬁned as

E2 =

−

(cid:20)

u′∂xyJf, ∂yyJf
2
h

u′′∂xJf, ∂yyJf

i − h

i −

u′′′∂xJf, ∂yJf
2
h

i
6u′u′′′

u′′∂yyf, ∂xyJf
4
h

−

4
h

i −

u′′∂xJf,
+ 2
h

u′′
u′ (∂yJf

−

u′u′′′

(u′′)2

−
u′

∂xJf, ∂yJf

i − h

4(u′′)2

−
u′

∂yf, ∂xyJf

i

∂yyf )

i − h

u′′∂xJf,

u′u′′′

2(u′′)2

−
(u′)2

∂yf

.
i
(cid:21)

(3.13)

Lastly, for the γ-term we argue as in (2.10) and obtain

1
2

d
dt k

u′∂xJf

2 + ν
k

u′∂xyJf
k

2
k

= ν

(u′u′′)′∂xJf, ∂xJf
h
(cid:20)

+

u′′′∂x(Jf
h

i

−

∂yf ), u′∂xJf

i

u′∂xy
2
h

−

(cid:18)

u′′
u′ (Jf

−

∂yf )

, u′∂xJf

(cid:19)

i
(cid:21)

= ν

(4(u′′)2 + u′u′′′)∂xJf, ∂xJf
h
(cid:20)

(4(u′′)2 + u′u′′′)∂xyf, ∂xJf

i − h

i

Therefore,

u′′∂xyf, u′∂xyJf
2
h

−

.

i
(cid:21)

1
2

d
dt k

u′∂xJf

2 + ν
k

u′∂xyJf
k

2 = νE3,
k

(3.14)

where

E3 =

(4(u′′)2 + u′u′′′)∂xJf, ∂xJf
h

i − h

(4(u′′)2 + u′u′′′)∂xyf, ∂xJf

u′′∂xyf, u′∂xyJf
2
h

. (3.15)
i

i −

Collecting (3.8), (3.10), (3.12) and (3.14) we end up with

d
dt J

+ ν

∂yJf
k

2 + να
∂yyJf
k
k

2 + β
k

u′∂xJf
k

2 + γν
k

u′∂xyJf
k

2
k

= νE0 + αE1 + νβE2 + νγE3.

(3.16)

To reach (3.5), we now have to estimate all the error terms in a suitable way.

3.3. Error estimates. In what follows, we will make heavy use of the assumption (H), keeping

track of the dependence on U of all the constants. The error term E0 in (3.9) is easily estimated as

E0| ≤
|

1
4 k

∂yJf

2 + 10U2
k

Jf
k

2 + 9U2
k

∂yf
k

2.
k

(3.17)

Turning to E1 in (3.11), we notice that the last term is essentially estimated as in (2.12), exploiting the
fact that

and obtaining

α2
βν

=

1
4

,

As for the other terms,
u′u′′′ + 2(u′′)2
(u′)2
U [3U
1
4 k

Jf
k
∂yyJf

h
(cid:12)
(cid:12)
(cid:12)
(cid:12)

≤

≤

α

u′∂xJf, ∂yJf
h

(cid:12)
(cid:12)

≤

i
(cid:12)
(cid:12)

ν
4 k

∂yJf

2 +
k

β
4 k

u′∂xJf

2.
k

(Jf

∂yf ), ∂yyJf

−
∂yyJf

+ 3U

kk
k
2 + 36U4
k

Jf
k

−

2
h
∂yyJf

u′′
u′ (∂yJf
∂yJf
+ 2
k
k
2 + 16U2
k

∂yf
k

i −

∂yf
k
kk
2 + 36U4
k

∂yyf ), ∂yyJf

∂yyJf

i
(cid:12)
(cid:12)
∂yyf
+ 2
(cid:12)
k
k
(cid:12)
2 + 16U2
k

∂yyf
k

kk
2.
k

kk
∂yJf
k

∂yyJf

]
k

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

11

Thus,

E1| ≤
α
|

∂yJf

ν
2 +
4 k
k
+ 36ανU4

2 +
k

β
u′∂xJf
4 k
2 + 36ανU4
k

αν
4 k

∂yyJf

2
k

∂yJf
k
We now deal with E2 in (3.13). Like in (2.14) and (2.15), recalling that

2 + 16ανU2
k

∂yf
k

Jf
k

2 + 16ανU2
k

∂yyf
k

2.
k

(3.18)

β2
αγ

=

1
8

,

we have

and

2νβ

u′∂xyJf, ∂yyJf

|h

να
4 k

∂yyJf

2 +
k

i| ≤

νγ
2 k

u′∂xyJf

2,
k

νβ

u′′∂xJf, ∂yyJf

|h

να
4 k

∂yyJf

2 +
k

i| ≤

νγ
8 k

u′′∂xJf

2.
k

The other terms are estimated as

(3.19)

(3.20)

(3.21)

u′′′∂xJf, ∂yJf
2
h
6u′u′′′

4(u′′)2

νβ

−

(cid:12)
(cid:12)
(cid:12)
(cid:12)
− h

−
u′

∂yf, ∂xyJf

u′′∂xJf,
+ 2
h

i

u′′∂yyf, ∂xyJf
4
h

i −

i −

u′u′′′

−
u′

4
h
u′′
u′ (∂yJf

(u′′)2

∂xJf, ∂yJf

i

∂yyf )
i

−

u′′∂xJf,

− h

βν

≤

h

u′u′′′

2(u′′)2

12U2

−
(u′)2
u′∂xJf
k
+ 2U2

kk
u′∂xJf
k

γν
8 k

β
4 k

≤

+

u′∂xJf

2 +
k
64β2νU2
γ

∂yyf
k

∂yf

i
(cid:12)
(cid:12)
+ 4U
(cid:12)
(cid:12)

∂yJf

k
∂yyf

kk
k
u′∂xyJf

u′∂xyJf
k
+ 3U3

kk
u′∂xJf
k

kk
2 + 1152βν2U4
k

∂yf

k
i
∂yJf
k

2 + 27βν2U6
k

∂yf
k

2 + 12βν2U4
k

∂yyf
k

2.
k

∂yyf

+ 10U2

u′∂xyJf
k

∂yf

kk

k

k

2 +
k

400β2νU4
γ

∂yf
k

2
k

Taking into account (3.19) and collecting (3.20), (3.21) and the estimates above, we have

νβ

5νγ

E2| ≤
|

∂yyJf

να
2 k
+ U2 νγ
8 k
+ 27βν2U6

8 k
2 + 1152βν2U4
k
2 + 12βν2U4
∂yf
k
k
Lastly, looking at (3.15), we have

2 +
k
u′∂xJf

2 +
k

β
4 k
∂yJf
k
∂yyf
k

2.
k

u′∂xyJf

u′∂xJf

2
k
2 + 50ανU4
k

∂yf
k

2 + 8ανU2
k

∂yyf
k

2
k

(3.22)

=

E3|
|

≤

≤

(4(u′′)2 + u′u′′′)∂xJf, ∂xJf
h
5U2
u′∂xJf
k
1
u′∂xJf
8 k
k

2 + 5U2
k
2 + 7U2
k

u′∂xJf
k
u′∂xyJf

i − h

(4(u′′)2 + u′u′′′)∂xyf, ∂xJf
u′∂xyf

i −
u′∂xyf

+ U

kk
2 + 8U2
k

u′∂xyJf
k
k
u′∂xyf
k

2.
k

kk

u′′∂xyf, u′∂xyJf
2
h

i

(3.23)

k

Now that all the errors have been properly controlled, we are ready to prove Proposition 3.1.

3.4. Proof of Proposition 3.1. Collecting (3.17), (3.18), (3.22) and (3.23) into (3.16) we have

d
dt J

+

≤

∂yyJf

∂yJf

ν
2 +
2 k
k
1168U6ν

να
4 k
Jf
(1 + α)
k
∂yf
+ (1 + α + βν)
k

β
2 k

2 +
k

u′∂xJf

2 +
k
2 + (α + βν)
∂yJf
k
k
2 + (α + βν)
∂yyf
k
k

γν
4 k
2 + γ
k
2 + γ
k

(cid:2)

u′∂xJf
k
2
u′∂xyf
k
k

u′∂xyJf

2
k
2
k
.

(3.24)

Recall that νk−1

≤

1 and that (2.1)-(2.2) in particular implies that

(cid:3)

β0 ≤

α0 ≤

1.

12

M. COTI ZELATI

Computing all the coefﬁcients of the above errors, we have

1 + α

2,

≤

α + βν

2α

≤

≤

2α0,

1 + α + βν

3,

≤

so that
d
dt J

+

∂yJf

ν
2 +
2 k
k
3504U6ν

Jf
k

≤

2 +
k
∂yJf

β
2 k
2 + γ
k

u′∂xJf

2 +
k
u′∂xJf
k

γν
4 k

u′∂xyJf

2
k
2 + α
∂yyf
k
k

2 +
k

∂yf
k

(cid:2)

In light of the restriction νk−1

ν0 given by (3.4), we have
ν2/3
k2/3 β
Using once more the expression of α0 in (2.2), (3.24) becomes

7008U8
β0

u′∂xJf
k

3504νU6

Jf
k

2
k

≤

(cid:3)

(cid:2)

να
∂yyJf
4 k
2 + α0k
k
≤
2 + γ
k

2 + γ
k

u′∂xyf
k

2
k

.

(cid:3)

u′∂xJf
k

2
k

≤

β
4 k

u′∂xJf

2,
k

d
dt J

2 +
k
2 + α
∂yyf
k
k
We now proceed as we did after (2.18), arriving after a few easy computations at

2 +
k
u′∂xyf
k

ν
2 +
4 k
k
3504U6ν

β
4 k
2 + γ
k

να
4 k

γν
4 k

u′∂xJf

∂yf
k

∂yyJf

∂yJf

2
k

≤

+

.

u′∂xyJf

2
k

(cid:3)

d
dt J

+

(cid:2)
β0
16U2 ν1/3k2/3
J
3504U6ν
∂yf
k

+

να
4 k

∂yyJf

2 +
k
2 + γ
k

γν
4 k
u′∂xyf
k

u′∂xyJf

2
k

.

2
k

(cid:3)

2 + α
∂yyf
≤
k
k
This is equivalent to (3.5), and therefore the proof is over.

(cid:2)

4. Weighted estimates in the energy norm

The Fourier-localized version of Theorem 1.1 is the following result.
THEOREM 4.1. There exist C0 ≥

1 and ε0, ν0 ∈

[0, ν0] we have the enhanced diffusion estimate

(0, 1) only depending on U such that if νk−1

∈

and the stable mixing estimate

fk(t)
k

ku′

C0e−ε0ν1/3k2/3t

≤

f in
k ku′,
k

t

∀

≥

0,

f in
k ku′ +
k
In particular, if ν = 0 we obtain the inviscid mixing estimate

fk(t)
k

k ˙H −1

C0

≤

(cid:2)

e−ε0ν1/3k2/3t
1 + (kt)2

p

fk(t)
k

k ˙H −1

≤

C0
1 + (kt)2

f in
k ku′ +
k

∂yf in
k

k ku′

All the constants can be computed explicitly.

p

(cid:2)

(cid:3)

,

(cid:3)

t

∀

≥

0.

∂yf in
k

k ku′

,

t

∀

≥

0.

(4.1)

(4.2)

PROOF OF THEOREM 4.1. We will restrict ourselves to the proof of (4.2). The proof of (4.1) is
analogous, and we will only highlight the differences whenever they arise. Again, dependences on k of
various functions are forgotten during the proof. Set

δ0 :=

4

×

1
3504U6 .

From (2.5) and the above (3.5) we deduce in particular that
d
dt

[Φ + δ0J

] + 2ε0ν1/3k2/3 [Φ + δ0J

(4.3)

(4.4)

0.

]

≤

By combining (2.7), (3.8), (3.17) and (4.3), we ﬁnd that

d
dt

f
k
(cid:2)

Since

2 + δ0k
k

Jf

2
k

+ ν

∂yf
2
k

2 + δ0k∇
k

Jf

2
k

ν
6U2 k

Jf

2.
k

≤

(cid:3)
2
k

Jf
k

(cid:2)

∂yf
2
k

2 + 2k2t2U2
k

f
k

≤

(cid:3)
2,
k

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

13

we ﬁnd that

2 + δ0k
2 + δ0k
k
k
In a similar manner, (2.10), (3.14), (3.23) and (4.3) imply that

∂yf
k

2
k

f
k

+ ν

Jf

(cid:2)

(cid:3)

(cid:2)

∂yJf

d
dt

1
3

≤

νk2t2

f
k

2.
k

2
k

(cid:3)

(4.5)

2
k
In particular, dividing everything by k2, an application of the Gronwall lemma gives

2 + δ0k
k

2 + δ0k
k

u′∂xf
k

u′∂xf
k

u′∂xJf

u′∂xJf

7U2ν

2
k

≤

(cid:2)

(cid:3)

(cid:2)

d
dt

.

(cid:3)

2 + δ0k
u′f (t)
k
k

2
u′Jf (t)
k

≤

e7U2νt

u′f in
k
(cid:2)

2 + δ0k
k

u′∂yf in

2
k

,

(cid:3)

t

∀

≥

0.

(4.6)

Deﬁne

Tν,k =

1
ν1/3k2/3 .

We divide the proof in two cases.

Case t
to arrive at

≥

Tν,k. We integrate (4.5) on (0, Tν,k) and use that Jf (0) = ∂yf in and that

f (t)
k

f in

k ≤ k

k

Tν,k

ν

0

Z

(cid:2)

2 + δ0k
∂yf (t)
k
k

2
∂yJf (t)
k

dt

≤

(cid:3)

≤

Tν,k

t2

νk2

1
2dt +
f (t)
3
k
k
0
Z
f in
f in
2 +
νk2T 3
ν,kk
k
k
∂yf in
2 + δ0k
f in
k
k
(0, Tν,k) such that
(cid:2)

f in
k
2 + δ0k
k
2
.
k

∂yf in

2 + δ0k
k
∂yf in

2
k

2
≤
Thus, by the mean value theorem there exists t⋆ ∈
(cid:3)
2 + δ0k
2
2 + δ0k
∂yf (t⋆)
∂yJf (t⋆)
k
k
k
k
Rewriting and keeping in mind (2.1) and that α0 ≤
1, it follows that
(cid:2)
2
Jf (t⋆)
k
k∇

2 + δ0k∇
f (t⋆)
k

2 + δ0k
k

(cid:2)
f in
k

f in
k

νTν,k

≤

≤

α

2

2

(cid:3)

On the other hand, by integrating (4.5) on (0, t⋆) we have

(cid:2)

(cid:3)

(cid:2)

∂yf in

2
k

.

∂yf in

(cid:3)

.

2
k

(cid:3)

2 + δ0k
f (t⋆)
k
k

2
Jf (t⋆)
k

≤

≤

≤

t⋆

νk2

1
3
0
Z
νk2T 3
ν,kk
f in
k

2

t2

2dt +
f (t)
k
k
f in
f in
2 +
k
k
∂yf in
2 + δ0k
k

f in
2 + δ0k
k
k
∂yf in
2 + δ0k
k
2
.
k

2
k

∂yf in

2
k

2
k

(4.7)

(4.8)

Moreover, by (4.6) and the restriction (3.4), we also deduce that

(cid:3)

2 + δ0k
u′f (t⋆)
k
k

2
u′Jf (t⋆)
k

≤

e7U2νTν,k

Now, using that from (4.4) we know that Φ + δ0J
(4.8) and (4.9) (and the fact that γ0 ≤

1) that

(cid:2)

(cid:2)
u′f in
k

u′∂yf in

2 + δ0k
k

2
.
k
(4.9)
(cid:3)
is decreasing, we have from (2.4), (3.3) and (4.7) and

2 + δ0k
k

u′f in
k

u′∂yf in

2
k

≤

2

(cid:2)

(cid:3)

Φ(Tν,k) + δ0J

(Tν,k)

≤

≤

≤

≤

≤

(t⋆)
Φ(t⋆) + δ0J
1
2 + δ0k
2 + δ0k
2) + 3α(
f (t⋆)
2(
Jf (t⋆)
∂yf (t⋆)
4
k
k
k
k
k
2)
u′∂xJf (t⋆)
2 + δ0k
u′∂xf (t⋆)
(cid:2)
+ 3γ(
k
k
k
(cid:3)
2 + δ0k
2) + 3α(
2 + δ0k
Jf (t⋆)
∂yf (t⋆)
f (t⋆)
2(
k
k
k
k
k
2)
u′Jf (t⋆)
2 + δ0k
u′f (t⋆)
(cid:2)
+ 3γ0(
k
k
k
∂yf in
2 + δ0k
u′f in
2 +
2 + δ0k
f in
(cid:3)
k
k
k
k
k
2
∂yf in
2
f in
,
u′ + δ0k
u′
k
k
k

u′∂yf in

2
k

1
4

2

2

(cid:3)

(cid:2)

(cid:2)

(cid:3)

2)
∂yJf (t⋆)
k

2)
∂yJf (t⋆)
k

(4.10)

14

M. COTI ZELATI

where the norm
that

k · ku′ is deﬁned in (1.9). Thus, for t

≥

Tν,k we have from (2.4), (3.3), (4.4) and (4.10)

δ0γ0
4

(cid:2)

2
u′ +
f (t)
k
k

2
Jf (t)
u′
k
k

(t)

Φ(t) + δ0J
e−2ε0ν1/3k2/3(t−Tν,k) [Φ(Tν,k) + δ0J
2e2ε0e−2ε0ν1/3k2/3t
2
u′ + δ0k
k

f in
k

(cid:3)

≤

≤

≤

(Tν,k)]

∂yf in

Thus since δ0 ≤
2
u′ +
f (t)
k
k
as we wanted.

1 and ε0 ≪
2
Jf (t)
u′
k
k

1,

≤

20
δ0γ0

e−2ε0ν1/3k2/3t

f in
k

2
u′ +
k

(cid:2)

(cid:2)
∂yf in
k

2
u′
k

,

(cid:3)

(4.11)

2
u′
k

.

(cid:3)

t

∀

≥

1
ν1/3k2/3

,

(cid:2)
f in
k

Case t

∈

[0, Tν,k). Notice that we are done if we can prove that

2
Jf (t)
u′
k
k
for some C > 0. From (4.5) and the Gronwall lemma, it follows that

2
u′ +
f (t)
k
k

∂yf in
k

2
u′ +
k

f in
k

2
u′
k

≤

C

(cid:3)

,

t

∀

≤

1
ν1/3k2/3 ,

2
Jf (t)
k

2 + δ0k
f (t)
k
k

2
k
Analogously, using (4.6) (this is essentially (4.9)), we also have
2 + δ0k
u′f (t)
k
k

(cid:2)
2
u′Jf (t)
k

2 + δ0k
k

u′f in
k

∂yf in

≤

≤

e

(cid:3)
2 + δ0k
k

eνk2t3

e

≤

f in
k

2 + δ0k
k

∂yf in

2
k

.

(cid:2)
u′∂yf in

(cid:3)

2
k

.

Hence,

(cid:2)

2
Jf (t)
u′
k
k
as we were trying to prove. Putting together (4.11) and (4.12) we have

2
u′ +
f (t)
k
k

∂yf in
k

2
u′ +
k

f in
k

2
u′
k

≤

(cid:3)

(cid:2)

,

e
δ0

(cid:3)
1
ν1/3k2/3 ,

t

∀

≤

(4.12)

2
u′ +
f (t)
k
k

2
Jf (t)
u′
k
k

≤

20
δ0γ0

e−2ε0ν1/3k2/3t

f in
k

2
u′ +
k

∂yf in
k

2
u′
k

,

t

∀

≥

0.

(4.13)

Having (4.13) at our disposal, we only need to invoke Lemma 3.2, so that (4.2) follows immediately.
in the
The proof of (4.1) is exactly the same, just not considering the parts involving the functional
above argument. The proof is therefore concluded.
(cid:3)

J

(cid:2)

(cid:3)

Acknowledgements. The author is indebted with T.M. Elgindi and K. Widmayer for endless and
inspiring discussions, especially concerning the use of the vector ﬁeld method in these problems, and
with G. Iyer, A. Mazzuccato and C. Nobili for clariﬁcations regarding the Batchelor scale.

References

[1] G. Alberti, G. Crippa, and A. L. Mazzucato, Exponential self-similar mixing by incompressible ﬂows, J. Amer. Math.

Soc. 32 (2019), no. 2, 445–490.

[2] K. Bajer, A. P Bassom, and A. D Gilbert, Accelerated diffusion in the centre of a vortex, Journal of Fluid Mechanics 437

(2001), 395–411.

[3] M. Beck and C. E. Wayne, Metastability and rapid convergence to quasi-stationary bar states for the two-dimensional

Navier-Stokes equations, Proc. Roy. Soc. Edinburgh Sect. A 143 (2013), no. 5, 905–927.

[4] J. Bedrossian, P. Germain, and N. Masmoudi, Dynamics near the subcritical transition of the 3D Couette ﬂow I: Below

threshold case, ArXiv e-prints (June 2015), available at 1506.03720.

[5] J. Bedrossian, P. Germain, and N. Masmoudi, Dynamics near the subcritical transition of the 3D Couette ﬂow II: Above

threshold case, ArXiv e-prints (June 2015), available at 1506.03721.

[6] J. Bedrossian and M. Coti Zelati, Enhanced dissipation, hypoellipticity, and anomalous small noise inviscid limits in

shear ﬂows, Arch. Ration. Mech. Anal. 224 (2017), no. 3, 1161–1204.

[7] J. Bedrossian, M. Coti Zelati, and N. Glatt-Holtz, Invariant Measures for Passive Scalars in the Small Noise Inviscid

Limit, Comm. Math. Phys. 348 (2016), no. 1, 101–127.

[8] J. Bedrossian, M. Coti Zelati, and V. Vicol, Vortex axisymmetrization, inviscid damping, and vorticity depletion in the

linearized 2D Euler equations, Ann. PDE 5 (2019), no. 1, Art. 4, 192.

[9] J. Bedrossian, P. Germain, and N. Masmoudi, On the stability threshold for the 3D Couette ﬂow in Sobolev regularity,

Ann. of Math. (2) 185 (2017), no. 2, 541–608.

[10] J. Bedrossian, N. Masmoudi, and V. Vicol, Enhanced dissipation and inviscid damping in the inviscid limit of the Navier-
Stokes equations near the two dimensional Couette ﬂow, Arch. Ration. Mech. Anal. 219 (2016), no. 3, 1087–1159.

STABLE MIXING ESTIMATES IN THE INFINITE P ´ECLET NUMBER LIMIT

15

[11] J. Bedrossian, V. Vicol, and F. Wang, The Sobolev stability threshold for 2D shear ﬂows near Couette, J. Nonlinear Sci.

28 (2018), no. 6, 2051–2075.

[12] A. Bressan, A lemma and a conjecture on the cost of rearrangements, Rend. Sem. Mat. Univ. Padova 110 (2003), 97–102.
[13] P. Constantin, A. Kiselev, L. Ryzhik, and A. Zlatos, Diffusion and mixing in ﬂuid ﬂow, Ann. of Math. (2) 168 (2008),

no. 2, 643–674.

[14] M. Coti Zelati, M. G. Delgadino, and T. M. Elgindi, On the relation between enhanced dissipation time-scales and mixing

rates, to appear in Comm. Pure Appl. Math., ArXiv e-prints (June 2018), available at 1806.03258.

[15] M. Coti Zelati and M. Dolce, Separation of time-scales in drift-diffusion equations on R2, arXiv e-prints (July 2019),

available at 1907.04012.

[16] M. Coti Zelati, T. M. Elgindi, and K. Widmayer, Enhanced dissipation in the Navier-Stokes equations near the Poiseuille

ﬂow, arXiv e-prints (Jan. 2019), available at 1901.01571.

[17] M. Coti Zelati and C. Zillinger, On degenerate circular and shear ﬂows: the point vortex and power law circular ﬂows,

Comm. Partial Differential Equations 44 (2019), no. 2, 110–155.

[18] G. Crippa and C. De Lellis, Estimates and regularity results for the DiPerna-Lions ﬂow, J. Reine Angew. Math. 616

(2008), 15–46.

[19] G. Crippa, R. Luc`a, and C. Schulze, Polynomial mixing under a certain stationary Euler ﬂow, Phys. D 394 (2019), 44–55.
[20] W. Deng, Resolvent estimates for a two-dimensional non-self-adjoint operator, Commun. Pure Appl. Anal. 12 (2013),

no. 1, 547–596.

[21] B Dubrulle and S Nazarenko, On scaling laws for the transition to turbulence in uniform-shear ﬂows, Euro. Phys. Lett.

27 (1994), no. 2, 129.

[22] T. Gallay, Enhanced dissipation and axisymmetrization of two-dimensional viscous vortices, Arch. Ration. Mech. Anal.

230 (2018), no. 3, 939–975.

[23] E. Grenier, T. T. Nguyen, F. Rousset, and A. Soffer, Linear inviscid damping and enhanced viscous dissipation of shear

ﬂows by using the conjugate operator method, ArXiv e-prints (Apr. 2018), available at 1804.08291.

[24] S. Ibrahim, Y. Maekawa, and N. Masmoudi, On pseudospectral bound for non-selfadjoint operators and its application

to stability of Kolmogorov ﬂows, ArXiv e-prints (Oct. 2017), available at 1710.05132.

[25] G. Iyer, A. Kiselev, and X. Xu, Lower bounds on the mix norm of passive scalars advected by incompressible enstrophy-

constrained ﬂows, Nonlinearity 27 (2014), no. 5, 973–985.

[26] P.-E. Jabin, Critical non-Sobolev regularity for continuity equations with rough velocity ﬁelds, J. Differential Equations

260 (2016), no. 5, 4739–4757.

[27] L. Kelvin, Stability of ﬂuid motion: rectilinear motion of viscous ﬂuid between two parallel plates, Phil. Mag. 24 (1887),

no. 5, 188–196.

[28] M. Latini and A. J. Bernoff, Transient anomalous diffusion in Poiseuille ﬂow, Journal of Fluid Mechanics 441 (2001),

399–411.

[29] T. Li, D. Wei, and Z. Zhang, Pseudospectral and spectral bounds for the Oseen vortices operator, ArXiv e-prints (Jan.

2017), available at 1701.06269.

[30] T. Li, D. Wei, and Z. Zhang, Pseudospectral bound and transition threshold for the 3D Kolmogorov ﬂow, arXiv e-prints

(Jan. 2018), available at 1801.05645.

[31] Z. Lin, J.-L. Thiffeault, and C. R. Doering, Optimal stirring strategies for passive scalar mixing, J. Fluid Mech. 675

(2011), 465–476.

[32] E. Lunasin, Z. Lin, A. Novikov, A. Mazzucato, and C. R. Doering, Optimal mixing and optimal stirring for ﬁxed energy,

ﬁxed power, or ﬁxed palenstrophy ﬂows, J. Math. Phys. 53 (2012), no. 11, 115611, 15.

[33] C. J. Miles and C. R. Doering, Diffusion-limited mixing by incompressible ﬂows, Nonlinearity 31 (2018), no. 5,

2346–2350.

[34] O. Reynolds, An experimental investigation of the circumstances which determine whether the motion of water shall be

direct or sinuous, and of the law of resistance in parallel channels, Proc. R. Soc. Lond. 174 (1883), 935–982.

[35] P. B. Rhines and W. R. Young, How rapidly is a passive scalar mixed within closed streamlines?, Journal of Fluid

Mechanics 133 (1983), 133–145.

[36] C. Seis, Maximal mixing by incompressible ﬂuid ﬂows, Nonlinearity 26 (2013), no. 12, 3279–3289.
[37] L. Tao and J. Wu, The 2D Boussinesq equations with vertical dissipation and linear stability of shear ﬂows, J. Differential

Equations 267 (2019), no. 3, 1731–1747.

[38] C. Villani, Hypocoercivity, Mem. Amer. Math. Soc. 202 (2009), no. 950, iv+141.
[39] D. Wei and Z. Zhang, Transition threshold for the 3D Couette ﬂow in Sobolev space, ArXiv e-prints (Mar. 2018), available

at 1803.01359.

[40] D. Wei, Z. Zhang, and W. Zhao, Linear inviscid damping and enhanced dissipation for the Kolmogorov ﬂow, ArXiv

e-prints (Nov. 2017), available at 1711.01822.

[41] D. Wei and Z. Zhang, Enhanced dissipation for the Kolmogorov ﬂow via the hypocoercivity method, Sci. China Math. 62

(2019), no. 6, 1219–1232.

[42] D. Wei, Z. Zhang, and W. Zhao, Linear inviscid damping for a class of monotone shear ﬂow in Sobolev spaces, Comm.

Pure Appl. Math. 71 (2018), no. 4, 617–687.

[43] D. Wei, Z. Zhang, and W. Zhao, Linear inviscid damping and vorticity depletion for shear ﬂows, Ann. PDE 5 (2019),

no. 1, Art. 3, 101.

16

M. COTI ZELATI

[44] D. Wei, Z. Zhang, and H. Zhu, Linear inviscid damping for the β-plane equation, arXiv e-prints (Sep. 2018), available at

1809.03065.

[45] Y. Yao and A. Zlatos, Mixing and un-mixing by incompressible ﬂows, J. Eur. Math. Soc. (JEMS) 19 (2017), no. 7,

1911–1948.

[46] C. Zillinger, On geometric and analytic mixing scales: comparability and convergence rates for transport problems,

ArXiv e-prints (Apr. 2018), available at 1804.11299.

[47] C. Zillinger, Linear inviscid damping for monotone shear ﬂows in a ﬁnite periodic channel, boundary effects, blow-up

and critical Sobolev regularity, Arch. Ration. Mech. Anal. 221 (2016), no. 3, 1449–1509.

[48] C. Zillinger, Linear inviscid damping for monotone shear ﬂows, Trans. Amer. Math. Soc. 369 (2017), no. 12, 8799–8855.
[49] C. Zillinger, On circular ﬂows: linear stability and damping, J. Differential Equations 263 (2017), no. 11, 7856–7899.
