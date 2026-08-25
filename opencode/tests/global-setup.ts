import { FullConfig } from '@playwright/test';
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function globalSetup(config: FullConfig) {
  const auditDir = path.resolve(__dirname, '../..', 'Documents/PROJETOS/audits');
  if (!fs.existsSync(auditDir)) {
    fs.mkdirSync(auditDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const version = browser.version();
  await browser.close();

  console.log(`[Global Setup] Playwright Chromium ${version} ready`);
  console.log(`[Global Setup] Audit directory: ${auditDir}`);
}

export default globalSetup;