"""Fitness Breakdown Visualization for Genetic Music Evolution.

Provides tools to visualize and analyze fitness scores during evolution:
- Evolution curves (fitness over generations)
- Population diversity metrics
- Fitness component breakdowns
- Rhythm/melody pattern analysis
- Comparative analysis across layers

Usage:
    from fitness_visualizer import FitnessVisualizer
    
    viz = FitnessVisualizer()
    
    # During evolution
    for gen in range(generations):
        population = ga.evolve(...)
        viz.record_generation(population, generation=gen, layer_name="melody")
    
    # After evolution
    viz.plot_evolution_curve(layer_name="melody")
    viz.plot_fitness_breakdown(individual, layer_name="melody")
    viz.plot_population_diversity()
"""

import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from core.genetic import Individual
from core.music import Phrase


@dataclass
class GenerationSnapshot:
    """Snapshot of population at a specific generation."""
    generation: int
    best_fitness: float
    mean_fitness: float
    std_fitness: float
    diversity: float  # Genotype diversity measure
    population_size: int
    best_genome: Any = None
    fitness_components: Dict[str, float] = field(default_factory=dict)


@dataclass
class FitnessComponents:
    """Breakdown of fitness components for detailed analysis."""
    total: float
    intrinsic: float = 0.0
    context: float = 0.0
    harmony: float = 0.0
    rhythm: float = 0.0
    melody: float = 0.0
    components: Dict[str, float] = field(default_factory=dict)


class FitnessVisualizer:
    """Visualizer for genetic algorithm fitness analysis."""
    
    def __init__(self, track_diversity: bool = True):
        """Initialize the visualizer.
        
        Args:
            track_diversity: If True, compute and track population diversity metrics
        """
        self.track_diversity = track_diversity
        
        # Storage for evolution history
        self.history: Dict[str, List[GenerationSnapshot]] = defaultdict(list)
        
        # Component analyzers (set these to get detailed breakdowns)
        self.component_analyzers: Dict[str, Callable] = {}
        
        # Custom matplotlib style
        self._setup_style()
    
    def _setup_style(self):
        """Setup matplotlib style for consistent visualizations."""
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        
    def record_generation(
        self,
        population: List[Individual],
        generation: int,
        layer_name: str = "default",
        fitness_components: Optional[Dict[str, float]] = None,
    ):
        """Record a generation snapshot for later visualization.
        
        Args:
            population: Population of individuals (must have .fitness attribute)
            generation: Generation number
            layer_name: Name of the layer being evolved
            fitness_components: Optional dict of fitness component scores
        """
        if not population:
            return
        
        fitnesses = [ind.fitness for ind in population]
        
        snapshot = GenerationSnapshot(
            generation=generation,
            best_fitness=max(fitnesses),
            mean_fitness=np.mean(fitnesses),
            std_fitness=np.std(fitnesses),
            diversity=self._compute_diversity(population) if self.track_diversity else 0.0,
            population_size=len(population),
            best_genome=population[0].genome,
            fitness_components=fitness_components or {},
        )
        
        self.history[layer_name].append(snapshot)
    
    def _compute_diversity(self, population: List[Individual]) -> float:
        """Compute population diversity metric.
        
        For rhythm strings: Hamming distance between individuals
        For phrases: Note pitch variance
        """
        if len(population) < 2:
            return 0.0
        
        # Try to detect genome type
        genome = population[0].genome
        
        if isinstance(genome, str):
            # Rhythm string - use Hamming distance
            total_distance = 0
            count = 0
            for i in range(len(population)):
                for j in range(i + 1, len(population)):
                    g1, g2 = population[i].genome, population[j].genome
                    if len(g1) == len(g2):
                        distance = sum(c1 != c2 for c1, c2 in zip(g1, g2))
                        total_distance += distance / len(g1)
                        count += 1
            return total_distance / max(count, 1)
        
        elif isinstance(genome, Phrase):
            # Phrase - use pitch diversity
            pitches = []
            for ind in population:
                phrase_pitches = [n.pitch.value for n in ind.genome.notes if hasattr(n.pitch, 'value')]
                pitches.extend(phrase_pitches)
            return float(np.std(pitches)) if pitches else 0.0
        
        else:
            # Generic: use fitness variance as proxy
            fitnesses = [ind.fitness for ind in population]
            return float(np.std(fitnesses))
    
    def plot_evolution_curve(
        self,
        layer_name: str = "default",
        show_std: bool = True,
        show_diversity: bool = False,
        save_path: Optional[str] = None,
    ):
        """Plot fitness evolution over generations.
        
        Args:
            layer_name: Which layer to plot
            show_std: If True, show standard deviation as shaded area
            show_diversity: If True, plot diversity on secondary axis
            save_path: If provided, save plot to this path
        """
        if layer_name not in self.history or not self.history[layer_name]:
            print(f"No data for layer '{layer_name}'")
            return
        
        history = self.history[layer_name]
        generations = [s.generation for s in history]
        best_fit = [s.best_fitness for s in history]
        mean_fit = [s.mean_fitness for s in history]
        std_fit = [s.std_fitness for s in history]
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        # Plot best and mean fitness
        ax1.plot(generations, best_fit, 'b-', linewidth=2, label='Best Fitness', marker='o', markersize=4)
        ax1.plot(generations, mean_fit, 'g--', linewidth=1.5, label='Mean Fitness', alpha=0.7)
        
        # Show standard deviation as shaded area
        if show_std:
            mean_arr = np.array(mean_fit)
            std_arr = np.array(std_fit)
            ax1.fill_between(generations, mean_arr - std_arr, mean_arr + std_arr,
                           alpha=0.2, color='green', label='±1 Std Dev')
        
        ax1.set_xlabel('Generation', fontsize=12)
        ax1.set_ylabel('Fitness Score', fontsize=12)
        ax1.set_title(f'Evolution Curve - {layer_name.title()}', fontsize=14, fontweight='bold')
        ax1.legend(loc='lower right')
        ax1.grid(True, alpha=0.3)
        
        # Plot diversity on secondary axis
        if show_diversity and self.track_diversity:
            diversity = [s.diversity for s in history]
            ax2 = ax1.twinx()
            ax2.plot(generations, diversity, 'r:', linewidth=1.5, label='Diversity', alpha=0.6)
            ax2.set_ylabel('Population Diversity', fontsize=12, color='r')
            ax2.tick_params(axis='y', labelcolor='r')
            ax2.legend(loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved evolution curve to {save_path}")
        else:
            plt.show()
    
    def plot_fitness_breakdown(
        self,
        layer_name: str = "default",
        generation: int = -1,
        save_path: Optional[str] = None,
    ):
        """Plot breakdown of fitness components for a specific generation.
        
        Args:
            layer_name: Which layer to analyze
            generation: Which generation (-1 = last)
            save_path: If provided, save plot to this path
        """
        if layer_name not in self.history or not self.history[layer_name]:
            print(f"No data for layer '{layer_name}'")
            return
        
        history = self.history[layer_name]
        snapshot = history[generation]
        
        if not snapshot.fitness_components:
            print(f"No component breakdown available for generation {snapshot.generation}")
            return
        
        # Extract components
        components = snapshot.fitness_components
        names = list(components.keys())
        values = list(components.values())
        
        # Create horizontal bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(names)))
        bars = ax.barh(names, values, color=colors, edgecolor='black', linewidth=0.5)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 0.01, i, f'{val:.3f}', va='center', fontsize=10)
        
        ax.set_xlabel('Score', fontsize=12)
        ax.set_title(f'Fitness Breakdown - {layer_name.title()} (Gen {snapshot.generation})', 
                    fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1.1)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved fitness breakdown to {save_path}")
        else:
            plt.show()
    
    def plot_population_diversity(
        self,
        layer_name: str = "default",
        save_path: Optional[str] = None,
    ):
        """Plot population diversity over time.
        
        Args:
            layer_name: Which layer to plot
            save_path: If provided, save plot to this path
        """
        if not self.track_diversity:
            print("Diversity tracking is disabled. Enable it in constructor.")
            return
        
        if layer_name not in self.history or not self.history[layer_name]:
            print(f"No data for layer '{layer_name}'")
            return
        
        history = self.history[layer_name]
        generations = [s.generation for s in history]
        diversity = [s.diversity for s in history]
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        ax.plot(generations, diversity, 'purple', linewidth=2, marker='s', markersize=4)
        ax.fill_between(generations, diversity, alpha=0.3, color='purple')
        
        ax.set_xlabel('Generation', fontsize=12)
        ax.set_ylabel('Diversity Metric', fontsize=12)
        ax.set_title(f'Population Diversity - {layer_name.title()}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Add annotation for diversity trend
        if len(diversity) > 1:
            trend = "increasing" if diversity[-1] > diversity[0] else "decreasing"
            change = abs(diversity[-1] - diversity[0])
            ax.text(0.02, 0.98, f'Trend: {trend}\nChange: {change:.3f}',
                   transform=ax.transAxes, va='top', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved diversity plot to {save_path}")
        else:
            plt.show()
    
    def plot_multi_layer_comparison(
        self,
        layer_names: Optional[List[str]] = None,
        metric: str = "best_fitness",
        save_path: Optional[str] = None,
    ):
        """Compare evolution across multiple layers.
        
        Args:
            layer_names: List of layers to compare (None = all)
            metric: Which metric to compare ('best_fitness', 'mean_fitness', 'diversity')
            save_path: If provided, save plot to this path
        """
        if layer_names is None:
            layer_names = list(self.history.keys())
        
        if not layer_names:
            print("No layers to compare")
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(layer_names)))
        
        for i, layer_name in enumerate(layer_names):
            if layer_name not in self.history:
                continue
            
            history = self.history[layer_name]
            generations = [s.generation for s in history]
            
            if metric == "best_fitness":
                values = [s.best_fitness for s in history]
                ylabel = "Best Fitness"
            elif metric == "mean_fitness":
                values = [s.mean_fitness for s in history]
                ylabel = "Mean Fitness"
            elif metric == "diversity":
                values = [s.diversity for s in history]
                ylabel = "Diversity"
            else:
                print(f"Unknown metric: {metric}")
                return
            
            ax.plot(generations, values, color=colors[i], linewidth=2, 
                   label=layer_name, marker='o', markersize=3)
        
        ax.set_xlabel('Generation', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(f'{ylabel} Comparison Across Layers', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved comparison plot to {save_path}")
        else:
            plt.show()
    
    def plot_rhythm_heatmap(
        self,
        layer_name: str = "default",
        num_snapshots: int = 10,
        save_path: Optional[str] = None,
    ):
        """Plot rhythm evolution as a heatmap over time.
        
        Shows how rhythm patterns change across generations.
        
        Args:
            layer_name: Which layer to visualize
            num_snapshots: Number of generation snapshots to show
            save_path: If provided, save plot to this path
        """
        if layer_name not in self.history or not self.history[layer_name]:
            print(f"No data for layer '{layer_name}'")
            return
        
        history = self.history[layer_name]
        
        # Sample snapshots evenly across generations
        indices = np.linspace(0, len(history) - 1, min(num_snapshots, len(history)), dtype=int)
        snapshots = [history[i] for i in indices]
        
        # Extract rhythm strings (only works for rhythm evolution)
        rhythms = []
        gen_labels = []
        for snapshot in snapshots:
            if isinstance(snapshot.best_genome, str):
                rhythms.append([int(c) for c in snapshot.best_genome])
                gen_labels.append(f"Gen {snapshot.generation}")
            else:
                print("Rhythm heatmap only works for rhythm (string) genomes")
                return
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        
        rhythm_array = np.array(rhythms)
        im = ax.imshow(rhythm_array, cmap='YlOrRd', aspect='auto', interpolation='nearest')
        
        # Set ticks
        ax.set_yticks(range(len(gen_labels)))
        ax.set_yticklabels(gen_labels)
        ax.set_xlabel('Beat Position', fontsize=12)
        ax.set_ylabel('Generation', fontsize=12)
        ax.set_title(f'Rhythm Evolution Heatmap - {layer_name.title()}', fontsize=14, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Subdivisions', fontsize=11)
        
        # Annotate cells with values
        for i in range(len(rhythms)):
            for j in range(len(rhythms[i])):
                text = ax.text(j, i, rhythms[i][j],
                             ha="center", va="center", color="black", fontsize=8)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved rhythm heatmap to {save_path}")
        else:
            plt.show()
    
    def plot_all_metrics_dashboard(
        self,
        layer_name: str = "default",
        save_path: Optional[str] = None,
    ):
        """Create a comprehensive dashboard with all metrics.
        
        Args:
            layer_name: Which layer to visualize
            save_path: If provided, save plot to this path
        """
        if layer_name not in self.history or not self.history[layer_name]:
            print(f"No data for layer '{layer_name}'")
            return
        
        history = self.history[layer_name]
        generations = [s.generation for s in history]
        best_fit = [s.best_fitness for s in history]
        mean_fit = [s.mean_fitness for s in history]
        diversity = [s.diversity for s in history] if self.track_diversity else None
        
        # Create 2x2 subplot grid
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Best Individual Characteristics Over Time
        ax1 = plt.subplot(2, 2, 1)
        if history[0].best_genome is not None:
            genome = history[0].best_genome
            
            # For rhythm strings - track rhythm metrics over time
            if isinstance(genome, str):
                from fitness.rhythm import (
                    rhythm_density, rhythm_complexity, rhythm_syncopation,
                    rhythm_groove, rhythm_rest_ratio
                )
                
                densities = []
                complexities = []
                syncopations = []
                grooves = []
                rest_ratios = []
                
                for snap in history:
                    if isinstance(snap.best_genome, str):
                        rhythm = snap.best_genome
                        densities.append(rhythm_density(rhythm))
                        complexities.append(rhythm_complexity(rhythm))
                        syncopations.append(rhythm_syncopation(rhythm))
                        grooves.append(rhythm_groove(rhythm))
                        rest_ratios.append(rhythm_rest_ratio(rhythm))
                
                ax1.plot(generations, densities, label='Density', linewidth=2, marker='o', markersize=3)
                ax1.plot(generations, complexities, label='Complexity', linewidth=2, marker='s', markersize=3)
                ax1.plot(generations, syncopations, label='Syncopation', linewidth=2, marker='^', markersize=3)
                ax1.plot(generations, grooves, label='Groove', linewidth=2, marker='d', markersize=3)
                ax1.plot(generations, rest_ratios, label='Rest Ratio', linewidth=2, marker='v', markersize=3)
                
                ax1.set_ylabel('Metric Value')
                ax1.set_title('Rhythm Characteristics Evolution', fontweight='bold')
                
            # For phrases - track melodic metrics
            elif isinstance(genome, Phrase):
                from fitness.base import note_variety, rest_ratio, interval_smoothness
                
                varieties = []
                smoothnesses = []
                rest_ratios = []
                
                for snap in history:
                    if isinstance(snap.best_genome, Phrase):
                        phrase = snap.best_genome
                        varieties.append(note_variety(phrase))
                        smoothnesses.append(interval_smoothness(phrase))
                        rest_ratios.append(rest_ratio(phrase))
                
                ax1.plot(generations, varieties, label='Note Variety', linewidth=2, marker='o', markersize=3)
                ax1.plot(generations, smoothnesses, label='Smoothness', linewidth=2, marker='s', markersize=3)
                ax1.plot(generations, rest_ratios, label='Rest Ratio', linewidth=2, marker='^', markersize=3)
                
                ax1.set_ylabel('Metric Value')
                ax1.set_title('Melody Characteristics Evolution', fontweight='bold')
                
            # For chord progressions - track chord metrics
            elif hasattr(genome, 'chords'):  # ChordProgression type
                from fitness.chords import (
                    chord_variety, root_motion_smoothness, seventh_chord_bonus,
                    repetitive_pattern_score, functional_harmony_score
                )
                
                varieties = []
                smoothnesses = []
                seventh_scores = []
                functional_scores = []
                repetitive_scores = []
                
                for snap in history:
                    if snap.best_genome is not None and hasattr(snap.best_genome, 'chords'):
                        prog = snap.best_genome
                        varieties.append(chord_variety(prog))
                        smoothnesses.append(root_motion_smoothness(prog))
                        seventh_scores.append(seventh_chord_bonus(prog))
                        functional_scores.append(functional_harmony_score(prog))
                        repetitive_scores.append(repetitive_pattern_score(prog))
                
                ax1.plot(generations, varieties, label='Variety', linewidth=2, marker='o', markersize=3)
                ax1.plot(generations, smoothnesses, label='Smooth Motion', linewidth=2, marker='s', markersize=3)
                ax1.plot(generations, seventh_scores, label='7th Chords', linewidth=2, marker='^', markersize=3)
                ax1.plot(generations, functional_scores, label='Functional', linewidth=2, marker='d', markersize=3)
                ax1.plot(generations, repetitive_scores, label='Repetition', linewidth=2, marker='v', markersize=3)
                
                ax1.set_ylabel('Metric Value')
                ax1.set_title('Chord Characteristics Evolution', fontweight='bold')
            else:
                ax1.text(0.5, 0.5, 'Genome type not supported for characteristic tracking',
                        ha='center', va='center', transform=ax1.transAxes)
            
            ax1.set_xlabel('Generation')
            ax1.legend(loc='best', fontsize=9)
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'No genome data available',
                    ha='center', va='center', transform=ax1.transAxes)
        
        # 2. Population diversity
        ax2 = plt.subplot(2, 2, 2)
        if diversity:
            ax2.plot(generations, diversity, 'purple', linewidth=2, marker='s', markersize=4)
            ax2.fill_between(generations, diversity, alpha=0.3, color='purple')
            ax2.set_xlabel('Generation')
            ax2.set_ylabel('Diversity')
            ax2.set_title('Population Diversity', fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # Add trend annotation
            if len(diversity) > 1:
                trend = "increasing" if diversity[-1] > diversity[0] else "decreasing"
                change = abs(diversity[-1] - diversity[0])
                ax2.text(0.02, 0.98, f'Trend: {trend}\nChange: {change:.3f}',
                       transform=ax2.transAxes, va='top', fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        else:
            ax2.text(0.5, 0.5, 'Diversity tracking disabled', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        # 3. Convergence indicator (plateau detection)
        ax3 = plt.subplot(2, 2, 3)
        if len(best_fit) > 1:
            # Calculate rolling improvement (last 5 generations)
            window = min(5, len(best_fit) // 2)
            improvements = np.diff(best_fit)
            rolling_improvement = []
            for i in range(len(improvements)):
                start = max(0, i - window + 1)
                rolling_improvement.append(np.mean(improvements[start:i+1]))
            
            ax3.plot(generations[1:], rolling_improvement, 'orange', linewidth=2)
            ax3.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5, label='No Improvement')
            ax3.fill_between(generations[1:], rolling_improvement, 0, 
                           where=np.array(rolling_improvement) > 0, 
                           alpha=0.3, color='green', label='Improving')
            ax3.fill_between(generations[1:], rolling_improvement, 0,
                           where=np.array(rolling_improvement) <= 0,
                           alpha=0.3, color='red', label='Stagnant')
            ax3.set_xlabel('Generation')
            ax3.set_ylabel(f'Avg Δ (last {window} gens)')
            ax3.set_title('Convergence Speed', fontweight='bold')
            ax3.legend(loc='best', fontsize=9)
            ax3.grid(True, alpha=0.3)
        
        # 4. Final generation fitness distribution
        ax4 = plt.subplot(2, 2, 4)
        final_gen_idx = len(best_fit) - 1
        if final_gen_idx >= 0:
            # Show fitness spread at final generation
            final_mean = mean_fit[final_gen_idx]
            final_best = best_fit[final_gen_idx]
            
            # Create a simple visualization of final population quality
            ax4.barh(['Best', 'Mean'], [final_best, final_mean], 
                    color=['gold', 'silver'], edgecolor='black', linewidth=1.5)
            
            # Add value labels
            ax4.text(final_best, 0, f' {final_best:.4f}', va='center', fontweight='bold')
            ax4.text(final_mean, 1, f' {final_mean:.4f}', va='center', fontweight='bold')
            
            # Show improvement from start
            initial_best = best_fit[0]
            improvement = final_best - initial_best
            improvement_pct = (improvement / max(initial_best, 0.001)) * 100
            
            ax4.set_xlabel('Fitness Score')
            ax4.set_title('Final Generation Quality', fontweight='bold')
            ax4.set_xlim(0, max(final_best, final_mean) * 1.2)
            ax4.grid(axis='x', alpha=0.3)
            
            # Add improvement annotation
            ax4.text(0.98, 0.02, 
                    f'Total Improvement:\n{improvement:+.4f} ({improvement_pct:+.1f}%)',
                    transform=ax4.transAxes, ha='right', va='bottom', fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        plt.suptitle(f'Evolution Dashboard - {layer_name.title()}', fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Saved dashboard to {save_path}")
        else:
            plt.show()
    
    def export_summary(self, layer_name: str = "default") -> Dict[str, Any]:
        """Export summary statistics for a layer's evolution.
        
        Returns:
            Dict with summary stats
        """
        if layer_name not in self.history or not self.history[layer_name]:
            return {}
        
        history = self.history[layer_name]
        best_fits = [s.best_fitness for s in history]
        mean_fits = [s.mean_fitness for s in history]
        
        return {
            "layer_name": layer_name,
            "total_generations": len(history),
            "initial_fitness": best_fits[0],
            "final_fitness": best_fits[-1],
            "improvement": best_fits[-1] - best_fits[0],
            "max_fitness": max(best_fits),
            "mean_of_means": np.mean(mean_fits),
            "convergence_rate": (best_fits[-1] - best_fits[0]) / len(best_fits) if len(best_fits) > 1 else 0,
            "final_diversity": history[-1].diversity if self.track_diversity else None,
        }
    
    def print_summary(self, layer_name: str = "default"):
        """Print a text summary of evolution statistics."""
        summary = self.export_summary(layer_name)
        
        if not summary:
            print(f"No data for layer '{layer_name}'")
            return
        
        print(f"\n{'='*60}")
        print(f"EVOLUTION SUMMARY: {summary['layer_name']}")
        print(f"{'='*60}")
        print(f"Total Generations:     {summary['total_generations']}")
        print(f"Initial Fitness:       {summary['initial_fitness']:.4f}")
        print(f"Final Fitness:         {summary['final_fitness']:.4f}")
        print(f"Improvement:           {summary['improvement']:+.4f}")
        print(f"Max Fitness Achieved:  {summary['max_fitness']:.4f}")
        print(f"Average Mean Fitness:  {summary['mean_of_means']:.4f}")
        print(f"Convergence Rate:      {summary['convergence_rate']:.6f} per gen")
        if summary['final_diversity'] is not None:
            print(f"Final Diversity:       {summary['final_diversity']:.4f}")
        print(f"{'='*60}\n")
    
    def clear_history(self, layer_name: Optional[str] = None):
        """Clear evolution history.
        
        Args:
            layer_name: If provided, clear only this layer. Otherwise clear all.
        """
        if layer_name:
            if layer_name in self.history:
                del self.history[layer_name]
                print(f"Cleared history for layer '{layer_name}'")
        else:
            self.history.clear()
            print("Cleared all history")
