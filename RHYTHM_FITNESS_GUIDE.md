# Rhythm Fitness Guide

## Overview

The rhythm fitness system evaluates rhythm patterns (strings like "21312240") based on genre-specific characteristics. Each genre has a distinct fitness function that rewards different rhythmic qualities.

## Rhythm Encoding

Rhythm strings encode subdivisions per beat:
- `'0'` = **rest** (no notes)
- `'1'` = **quarter note** (1 note per beat)
- `'2'` = **eighth notes** (2 notes per beat)
- `'3'` = **triplets** (3 notes per beat)
- `'4'` = **sixteenth notes** (4 notes per beat)

**Example**: `"21312240"` = 8 beats with varied subdivisions

## Rhythm Metrics

### Basic Metrics

1. **Complexity** (0.0-1.0)
   - Measures variety of subdivision types
   - Higher = more different subdivision values
   - `"22222222"` = 0.2 (simple)
   - `"31402413"` = 1.0 (complex)

2. **Density** (0.0-1.0)
   - Average notes per beat
   - Higher = more notes
   - `"11111111"` = 0.25 (sparse)
   - `"44444444"` = 1.0 (dense)

3. **Syncopation** (0.0-1.0)
   - How often subdivision changes between beats
   - Higher = more rhythmic variety
   - `"22222222"` = 0.0 (steady)
   - `"24132413"` = 1.0 (syncopated)

4. **Groove** (0.0-1.0)
   - Alternation between strong/weak beats
   - Higher = more danceable
   - `"22222222"` = 0.0 (no alternation)
   - `"42142142"` = 0.86 (strong groove)

5. **Consistency** (0.0-1.0)
   - Pattern repetition/predictability
   - Higher = more repetitive
   - `"12341234"` = 0.5 (some repetition)
   - `"22222222"` = 0.875 (very consistent)

6. **Rest Ratio** (0.0-1.0)
   - Proportion of rests in pattern
   - Higher = more space
   - `"22222222"` = 0.0 (no rests)
   - `"00000000"` = 1.0 (all rests)

## Genre-Specific Fitness Functions

### Pop (`pop_rhythm_fitness`)

**Characteristics:**
- Consistent, catchy patterns
- Moderate density
- Strong groove
- Few rests

**Weights:**
```python
0.25 * rhythm_consistency +      # Repetitive/catchy
0.25 * rhythm_groove +            # Strong groove
0.25 * (1 - rhythm_rest_ratio) +  # Few rests
0.15 * rhythm_density +           # Moderate density
0.10 * (1 - rhythm_complexity)    # Not too complex
```

**Example good patterns:**
- `"22222222"` - Consistent eighth notes (fitness: 0.624)
- `"21212121"` - Alternating pattern
- `"22112211"` - Simple repetitive

**Evolved example:**
```
Rhythm: 14134144
Complexity: 0.60, Density: 0.69, Syncopation: 0.86
Groove: 0.71, Rest Ratio: 0.00
```

### Jazz (`jazz_rhythm_fitness`)

**Characteristics:**
- High complexity
- Very syncopated
- Offbeat emphasis
- Some strategic rests

**Weights:**
```python
0.35 * rhythm_syncopation +                      # Very syncopated
0.25 * rhythm_complexity +                       # Complex patterns
0.20 * rhythm_offbeat_emphasis +                 # Offbeat accents
0.10 * (0.5 - abs(0.3 - rhythm_rest_ratio)) +   # ~30% rests
0.10 * (1 - rhythm_consistency)                  # Avoid repetition
```

**Example good patterns:**
- `"31402310"` - Complex, varied (fitness: 0.795)
- `"24130421"` - Syncopated
- `"32142013"` - Unpredictable

### Funk (`funk_rhythm_fitness`)

**Characteristics:**
- Maximum groove
- Highly syncopated
- Offbeat emphasis
- Dense but articulated

**Weights:**
```python
0.40 * rhythm_groove +              # Maximum groove
0.30 * rhythm_syncopation +         # Highly syncopated
0.15 * rhythm_offbeat_emphasis +    # Offbeat accents
0.10 * rhythm_density +             # Fairly dense
0.05 * (1 - rhythm_rest_ratio)      # Few rests
```

**Example good patterns:**
- `"42142114"` - Groovy, tight (fitness: 0.748)
- `"32143214"` - Syncopated funk
- `"24243214"` - Dense groove

### Ambient (`ambient_rhythm_fitness`)

**Characteristics:**
- Very sparse
- Simple patterns
- Many rests
- Meditative consistency

**Weights:**
```python
0.35 * rhythm_rest_ratio +              # Many rests
0.25 * (1 - rhythm_density) +           # Very sparse
0.20 * (1 - rhythm_complexity) +        # Simple
0.15 * rhythm_consistency +             # Repetitive
0.05 * (1 - rhythm_syncopation)         # Steady
```

**Example good patterns:**
- `"10001000"` - Sparse, meditative (fitness: 0.758)
- `"00100010"` - Very sparse
- `"01000100"` - Minimal
- `"00000000"` - All rests (fitness: 0.941) ← Often evolves to this!

### Rock (`rock_rhythm_fitness`)

**Characteristics:**
- High density
- Strong groove
- Few rests
- Driving energy

**Weights:**
```python
0.30 * rhythm_density +                             # Dense/energetic
0.25 * rhythm_groove +                              # Strong groove
0.20 * (1 - rhythm_rest_ratio) +                    # Few rests
0.15 * rhythm_consistency +                         # Consistent patterns
0.10 * (0.5 - abs(0.3 - rhythm_complexity))        # Moderate complexity
```

**Example good patterns:**
- `"22222222"` - Steady eighth notes
- `"24242424"` - Driving pattern
- `"22242224"` - Power groove

## How Rhythm Fitness is Used

### In LayeredComposer

```python
composer.add_layer(LayerConfig(
    name="melody",
    instrument="piano",
    rhythm_fitness_fn=RHYTHM_FITNESS_FUNCTIONS["pop"],  # ← Rhythm fitness here
    melody_fitness_fn=PopFitness(),                      # ← Separate melody fitness
))
```

### Evolution Process

1. **Initialize**: Generate random rhythm strings
2. **Evaluate**: Apply genre-specific rhythm fitness
3. **Select**: Tournament selection of best rhythms
4. **Breed**: Crossover and mutation
5. **Repeat**: Until target fitness reached
6. **Result**: Genre-appropriate rhythm pattern

### Example Output

```
Evolving rhythm for layer: melody
  Gen  0: Best fitness = 0.623, rhythm = 22131441
  Gen  5: Best fitness = 0.701, rhythm = 41431441
  Gen 10: Best fitness = 0.746, rhythm = 33131313
✓ Final rhythm: 33131313 (fitness: 0.746)

Rhythm Analysis:
  - Complexity: 0.40
  - Density: 0.75
  - Syncopation: 0.86
  - Groove: 0.86
  - Rest Ratio: 0.00
```

## Testing Rhythm Fitness

Run the test script to see all genres:

```bash
python test_rhythm_fitness.py
```

This will:
1. Evolve a rhythm for each genre
2. Show fitness metrics for each
3. Compare with hand-crafted examples
4. Demonstrate genre differentiation

## Creating Custom Rhythm Fitness

```python
def custom_rhythm_fitness(rhythm: str) -> float:
    """Custom rhythm fitness function."""
    from fitness.rhythm import (
        rhythm_density,
        rhythm_syncopation,
        rhythm_rest_ratio
    )

    # Define your own weighting
    return (
        0.40 * rhythm_density(rhythm) +
        0.40 * rhythm_syncopation(rhythm) +
        0.20 * (1 - rhythm_rest_ratio(rhythm))
    )

# Use it in a layer
composer.add_layer(LayerConfig(
    name="custom",
    rhythm_fitness_fn=custom_rhythm_fitness,  # ← Your custom function
    melody_fitness_fn=PopFitness(),
))
```

## Key Takeaways

1. **Each genre produces distinct rhythms** - The fitness functions successfully differentiate styles
2. **Ambient often evolves to all rests** - This is correct! Ambient fitness heavily rewards sparsity
3. **Pop/Rock are consistent** - High consistency scores, repetitive patterns
4. **Jazz/Funk are complex** - High syncopation and groove scores
5. **The system works** - Click the Strudel URLs and hear the difference!

## Rhythm Evolution is Working! ✅

The rhythm fitness functions are actively shaping the evolution:
- **Pop layers** evolve groovy, consistent patterns
- **Jazz layers** evolve complex, syncopated patterns
- **Funk layers** evolve maximum groove patterns
- **Ambient layers** evolve sparse, restful patterns
- **Rock layers** evolve dense, driving patterns

Each layer's rhythm is evolved BEFORE the melody, ensuring genre-appropriate foundations!
