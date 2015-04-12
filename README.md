# Life Extravaganza

This project is meant to bring a nice little eyecandy idea from the 1990s
to modern platforms. So far, I implemented a variant of the idea in Python,
but variants that work in a browser are much welcome.

## Quick start

Currently the program consists of [one file](game.py) only, with merely
about 500 lines. You simply run this file using python.

For this, you need a recent version of Python (either 2 or 3 is fine) as
well as [pygame](http://www.pygame.org).

## Back story

Once upon a time, a young fellow named Christian Kothe toyed around with
Turbo Pascal 7, coming up with a program that made for cool eyecandy.
It simulated and visualized protozoal lifeforms---for lack of a better
word called: `livators'---and their struggle for survival.

Livators, each one represented by a circle, wafted around the screen in
random motion, gathering nutrition. Nutrition was represented by grey pixels
of varying intensity, which corresponded to the nutritional value. Thereby
the livators could grow and eventually divide, and thus procreate. A livator
could also shrink, as motion depleted its resources, and then it would die,
in particular when the demand for nutrition exceeded its supply.

The livators were grouped into teams with different colors, and livators
from different teams were battling each other using advanced weaponry and
armoury, such as lasers, heat-seeking missiles, and shields. Visualization
mainly relied on particle effects, which were cheap given the MCGA resolution
and a clever use of the 256 color palette.

## Original vs. new

The current version is due to Matthias Büchse. It

* uses a higher resolution. It therefore
* has no particle effects.
* does not have lasers or shields.
* uses a torus surface as playing field instead of a rectangle. From the
  livator's point of view, the world has no boundaries. From the spectator's
  point of view, a livator that exits the screen on one side reenters it at
  the opposite side.

## Potential improvements

What might be done next, either to advance the implementation or the idea.
This could involve you!

### Bring it to the web

It would be cool to have an implementation in HTML 5/JavaScript, but I cannot
stomach JavaScript at all, nor its brethren CoffeeScript and the like.
Fortunately, there may be an alternative route towards such an implementation
that goes via C++, LLVM, and [emscripten](https://github.com/kripken/emscripten),
as demonstrated by Unreal Engine 4. Or one might even use
[empythoned](https://github.com/replit/empythoned).

### Come closer to the original version

For instance, one might use the original resolution and palette and then
interpolate. An example where this works well is ScummVM.

### Use modern graphics

It may or may not be appropriate for the underlying idea, but one could try and
use modern 3D graphics. For instance, if the world lies on a torus surface, why
not show the torus? Then again, any given time an estimated 50 % of the torus
surface would be occluded by other parts of the torus, so one would miss out on a
lot of the action.

Another idea would be to visualize the livators three-dimensionally, e.g., as
spheres. Finally, one could even make the whole world three-dimensional. As
stated above, this may, in the end, not be appealing at all.

### Incorporate genetics

Each livator's life is governed by a set of parameters:
* how long until a new missile becomes ready,
* average time of an acceleration phase,
* probability of starting an acceleration phase,
* the size at which to divide into two,
* the maximum size,
and probably others.

It might be interesting to introduce mutation into this scenario so as to
simulate survival of the fittest. However, the above-mentioned parameters do
not have an apparent phenotype, and they would be hard to visualize.

Going further, one might replace the concept of teams by species. As in real
life, it is hard to come up with a working definition of a species. It is simple
to define a metric on genes, that is, a notion of genetic distance. But it is
hard to derive an equivalence relation from such a metric: imagine three
livators A, B, and C, where A is close to B, B is close to C, but A is not
close to C. Then how can these livators be grouped into teams?

## License

This implementation is under [GPLv3](LICENSE). Christian's idea is under
[CC-BY-SA 4.0](http://creativecommons.org/licenses/by-sa/4.0/)
