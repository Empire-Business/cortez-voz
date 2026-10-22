import {
  DISTRIBUTION_PROFILES,
  type DistributionProfile,
  type DistributionTarget,
} from '../../../config/distributions.mjs';

export const CURRENT_DISTRIBUTION = __DISTRIBUTION_TARGET__ as DistributionTarget;

export function currentDistributionProfile(): DistributionProfile {
  return DISTRIBUTION_PROFILES[CURRENT_DISTRIBUTION];
}

export function applicationUpdatesSupported(
  packaged: boolean,
  target: DistributionTarget = CURRENT_DISTRIBUTION,
  disabledByEnvironment = process.env.VOICESTUDIO_DISABLE_UPDATER === '1',
): boolean {
  return false; // Cortez Voz updates only through the pinned Cortez installer.

}

export function runtimeSetupSupported(target: DistributionTarget = CURRENT_DISTRIBUTION): boolean {
  return DISTRIBUTION_PROFILES[target].runtimeCode === 'user-initiated-download';
}
