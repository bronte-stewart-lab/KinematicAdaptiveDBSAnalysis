clc; close all; clear all;

%%load Summit RC + S data
[unifiedDerivedTimes,...
    timeDomainData, timeDomainData_onlyTimeVariables, timeDomain_timeVariableNames,...
    AccelData, AccelData_onlyTimeVariables, Accel_timeVariableNames,...
    PowerData, PowerData_onlyTimeVariables, Power_timeVariableNames,...
    FFTData, FFTData_onlyTimeVariables, FFT_timeVariableNames,...
    AdaptiveData, AdaptiveData_onlyTimeVariables, Adaptive_timeVariableNames,...
    timeDomainSettings, powerSettings, fftSettings, eventLogTable,...
    metaData, stimSettingsOut, stimMetaData, stimLogSettings,...
    DetectorSettings, AdaptiveStimSettings, AdaptiveEmbeddedRuns_StimSettings,...
    versionInfo] = ProcessRCS(fullfile('data', 'Neural', 'DeviceNPC700519H'));

dataStreams = {timeDomainData, AdaptiveData};
[neural_rcs_data] = createCombinedTable(dataStreams, unifiedDerivedTimes, metaData);

%%load JAVA data (gait procressing outputs)

java_csv = readtable(fullfile('data', 'Java', 'data_RCS10_KaDBSI_fINaL.csv'), ...
    'ReadVariableNames', false);

state_vec = str2double(strrep(java_csv.Var1(7:7:height(java_csv),1), '"', ''));
arr_vec = str2double(strrep(java_csv.Var1(6:7:height(java_csv),1), '"', ''));
asym_vec = str2double(strrep(java_csv.Var2(6:7:height(java_csv),1), '"', ''));
freezeprob_vec = str2double(strrep(java_csv.Var3(6:7:height(java_csv),1), '"', ''));
time_vec = str2double(strrep(java_csv.Var3(7:7:height(java_csv),1), '"', ''));

%%match Java unix time to PST

java_unix_seconds = time_vec / 1000;
java_utc_time = datetime(java_unix_seconds, 'ConvertFrom', 'posixtime', 'TimeZone', 'UTC');
java_california_time = java_utc_time;
java_california_time.TimeZone = 'America/Los_Angeles';

%%stimulation amplitude and time

chanfn = sprintf('Adaptive_Ld%d_output', 0);
ydet = neural_rcs_data.(chanfn);
idxkeep = ~isnan(ydet);

time_neural = neural_rcs_data.localTime(idxkeep);
ycurrent = neural_rcs_data.Adaptive_CurrentProgramAmplitudesInMilliamps(idxkeep);
ycurrent = cell2mat(ycurrent);
ycurrent = ycurrent(:, 1:2);

yfreq = neural_rcs_data.Adaptive_StimRateInHz(idxkeep);

%% arrthmicty based control (patient specific threshold, Figure 3A-C)

arr_threshold = 0.09;

first_idx = find(~isnan(arr_vec), 1, 'first');
last_idx = find(~isnan(arr_vec), 1, 'last');

java_start = java_california_time(first_idx);
java_t_sec = seconds(java_california_time - java_start);
java_t_sec = java_t_sec(first_idx:last_idx);
arr_clipped = arr_vec(first_idx:last_idx);
state_clipped = state_vec(first_idx:last_idx);

neural_start = find(time_neural >= java_start, 1, 'first');
neural_end = find(time_neural <= java_california_time(last_idx), 1, 'last');
time_neural_clipped = time_neural(neural_start:neural_end);
time_neural_sec = seconds(time_neural_clipped - time_neural_clipped(1));
ycurrent_clipped = ycurrent(neural_start:neural_end, :);

set(0, 'DefaultAxesFontName', 'Helvetica');
set(0, 'DefaultAxesFontSize', 14);
set(0, 'DefaultTextFontName', 'Helvetica');
set(0, 'DefaultTextFontSize', 14);

figure('Position', [100, 100, 800, 600]);

ax1 = subplot(3,1,1);
hold on
plot(java_t_sec, arr_clipped, 'b', 'LineWidth', 2.5);
yline(arr_threshold, 'r--', 'LineWidth', 3.5);
ylabel('Arrhythmicity');
xlim([0 85]);

ax2 = subplot(3,1,2);
plot(java_t_sec, state_clipped, 'Color', [0.4940 0.1840 0.5560], 'LineWidth', 2.5);
yline(1, 'k--');
ylabel('State');
xlabel('Time (s)');
xlim([0 85]);

ax3 = subplot(3,1,3);
plot(time_neural_sec, ycurrent_clipped, 'Color', [0.8500 0.3250 0.0980], 'LineWidth', 2.5);
ylabel('Stim Amp (mA)');
xlim([0 85]);

linkaxes([ax1 ax2 ax3], 'x');
set(gcf, 'Color', 'w');

%%PFOG based controller (Figure 3D-F)

first_idx = find(~isnan(freezeprob_vec), 1, 'first');
last_idx = find(~isnan(freezeprob_vec), 1, 'last');

java_start = java_california_time(first_idx);
java_t_sec = seconds(java_california_time - java_start);
java_t_sec = java_t_sec(first_idx:last_idx);
freeze_clipped = freezeprob_vec(first_idx:last_idx);
state_clipped = state_vec(first_idx:last_idx);

neural_start = find(time_neural >= java_start, 1, 'first');
neural_end = find(time_neural <= java_california_time(last_idx), 1, 'last');
time_neural_clipped = time_neural(neural_start:neural_end);
time_neural_sec = seconds(time_neural_clipped - time_neural_clipped(1));
ycurrent_clipped = ycurrent(neural_start:neural_end, :);

figure('Position', [100, 100, 800, 600]);

ax1 = subplot(3,1,1);
hold on
plot(java_t_sec, freeze_clipped, 'b', 'LineWidth', 2.5);
yline(0.7, 'r--', 'LineWidth', 3.5);
yline(0.3, 'g--', 'LineWidth', 3.5);
ylabel('P(FOG)');
xlim([0 200]);

ax2 = subplot(3,1,2);
plot(java_t_sec, state_clipped, 'Color', [0.4940 0.1840 0.5560], 'LineWidth', 2.5);
yline(1, 'k--');
ylabel('State');
xlabel('Time (s)');
xlim([0 200]);

ax3 = subplot(3,1,3);
plot(time_neural_sec, ycurrent_clipped, 'Color', [0.8500 0.3250 0.0980], 'LineWidth', 2.5);
ylabel('Stim Amp (mA)');
xlim([0 200]);

linkaxes([ax1 ax2 ax3], 'x');
set(gcf, 'Color', 'w');
