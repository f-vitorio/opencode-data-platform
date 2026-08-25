import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('[Global Teardown] Cleanup complete');
}

export default globalTeardown;