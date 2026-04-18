import numpy as np
import matplotlib.pyplot as plt
import math


class SpikingNeuronNetwork:
    """
    Single-neuron Leaky Integrate-and-Fire (LIF) model
    with self-excitation and output synaptic current.
    """

    def __init__(self):
        # === Simulation parameters ===
        self.dt = 0.1       # Time step [ms]
        self.T = 500.0      # Total simulation time [ms]
        self.t = 0.0        # Current time

        # === Neuron parameters ===
        self.E_L = -70.0    # Resting potential [mV]
        self.V_th = -55.0   # Spike threshold [mV]
        self.V_reset = -70.0
        self.V_spike = -35.0
        self.C_m = 250.0    # Membrane capacitance [pF]
        self.tau_m = 10.0   # Membrane time constant [ms]
        self.t_ref = 2.0    # Refractory period [ms]

        # === Synaptic parameters ===
        self.tau_syn_ex = 2.0
        self.tau_syn_in = 2.0
        self.delay = 1.0
        self.w_ex = 1200.0
        self.w_in = 0.0
        self.w_out = 1000.0

        # === State variables ===
        self.V_m1 = self.E_L
        self.refractory_timer1 = 0.0
        self.V_m2 = self.E_L
        self.refractory_timer2 = 0.0
        self.V_m3 = self.E_L
        self.refractory_timer3 = 0.0
        self.V_m4 = self.E_L
        self.refractory_timer4 = 0.0

        self.I_input1 = 0.0
        self.I_input2 = 0.0

        # === Spike history ===
        self.spike_times1 = []
        self.spike_trace1 = []
        self.spike_times2 = []
        self.spike_trace2 = []
        self.spike_times3 = []
        self.spike_trace3 = []
        self.spike_times4 = []
        self.spike_trace4 = []

        # === Recording for plotting ===
        self.t_trace = []
        self.sineInput_trace = []
        self.I_input1_trace = []
        self.V_trace1 = []
        self.I_input2_trace = []
        self.V_trace2 = []
        self.I_input3_trace = []
        self.V_trace3 = []
        self.I_input4_trace = []
        self.V_trace4 = []
        self.I_syn_out_trace = []
    
    def update_neuron(self, V_m, refractory_timer, spike_times_self, S_input):

        spike = 0
        Sensory_input = S_input

        if refractory_timer > 0:
            refractory_timer -= self.dt
            V_m = self.V_reset
        else:
            # membrane integration
            dV = ((-(V_m - self.E_L) / self.tau_m) + (Sensory_input) / self.C_m) * self.dt
            V_m += dV

            # spike
            if V_m >= self.V_th:
                spike = 1
                V_m = self.V_spike
                refractory_timer = self.t_ref
                spike_times_self.append(self.t)

            # ====== C1: prune old spikes (speed fix) ======
            cutoff = self.t - 20.0  # keep only recent 20 ms
            spike_times_self[:] = [ts for ts in spike_times_self if ts > cutoff]
            #spike_times_other[:] = [ts for ts in spike_times_other if ts > cutoff]

        return V_m, refractory_timer, spike_times_self, spike

    def run(self):
        """Main simulation loop"""

        for t in np.arange(0, self.T, self.dt):
            self.t = t

            # === Sine wave input ===
            A = 1.0  # amplitude
            f = 1.25     # frequency
            dt_local = 0.01
            self.I_weight = 1000;
            
            self.sineInput = A * math.sin(2 * math.pi * f * t * dt_local)
            self.I_input1 = self.I_weight * self.sineInput
            self.I_input2 = self.I_weight * self.sineInput * 2.0
            self.I_input3 = self.I_weight * self.sineInput * -1
            self.I_input4 = self.I_weight * self.sineInput * -2.0

            # === Update neuron I1===
            self.V_m1, self.refractory_timer1, self.spike_times1, spike = self.update_neuron(
            self.V_m1, self.refractory_timer1, self.spike_times1, self.I_input1)
            
            # === Update neuron I2===
            self.V_m2, self.refractory_timer2, self.spike_times2, spike2 = self.update_neuron(
            self.V_m2, self.refractory_timer2, self.spike_times2, self.I_input2)
            
            # === Update neuron I3===
            self.V_m3, self.refractory_timer3, self.spike_times3, spike3 = self.update_neuron(
            self.V_m3, self.refractory_timer3, self.spike_times3, self.I_input3)
            
            # === Update neuron I4===
            self.V_m4, self.refractory_timer4, self.spike_times4, spike4 = self.update_neuron(
            self.V_m4, self.refractory_timer4, self.spike_times4, self.I_input4)


            # === Record signals ===
            self.t_trace.append(t)
            self.sineInput_trace.append(self.sineInput)
            self.V_trace1.append(self.V_m1)
            self.V_trace2.append(self.V_m2)
            self.V_trace3.append(self.V_m3)
            self.V_trace4.append(self.V_m4)
            self.spike_trace1.append(spike)
            self.spike_trace2.append(spike2)
            self.spike_trace3.append(spike3)
            self.spike_trace4.append(spike4)

        self.plot_results()

    def plot_results(self):
        """Plot results"""

        fig, axs = plt.subplots(5, 1, figsize=(10, 6), sharex=True)

        # Input current
        axs[0].plot(self.t_trace, self.sineInput_trace, linewidth=2, color='orange')
        axs[0].set_ylabel("Input")
        axs[0].set_ylim(-1.2, 1.2)
        axs[0].set_xlim(0, 350)

        # Membrane voltage
        axs[1].plot(self.t_trace, self.V_trace1, linewidth=1.5, color='lightblue')
        axs[1].set_ylabel("V_m_I1")
        axs[1].set_ylim(-120, -20)

        # Firing rate
        axs[2].plot(self.t_trace, self.V_trace2, linewidth=1.5, color='blue')
        axs[2].set_ylabel("V_m_I2")
        axs[2].set_ylim(-150, -20)
        
        # Synaptic output
        axs[3].plot(self.t_trace, self.V_trace3, linewidth=1.5, color='lightgreen')
        axs[3].set_ylabel("V_m_I3")
        axs[3].set_ylim(-120, -20)

        # Synaptic output
        axs[4].plot(self.t_trace, self.V_trace4, linewidth=1.5, color='green')
        axs[4].set_ylabel("V_m_I4")
        axs[4].set_xlabel("time step")
        axs[4].set_ylim(-150, -20)

        plt.tight_layout()
        plt.show()


# === Run ===
if __name__ == "__main__":
    net = SpikingNeuronNetwork()
    net.run()