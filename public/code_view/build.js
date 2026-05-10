// build.js - fixed alias error version
const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

const assetsDir = path.join(__dirname, 'assets');
if (!fs.existsSync(assetsDir)) {
  fs.mkdirSync(assetsDir, { recursive: true });
}

const stableConfig = {
  entryPoints: ['editor.js'],
  bundle: true,
  outfile: 'assets/bundle_editor.js',
  format: 'esm',
  platform: 'browser',
  target: ['es2020'],
  loader: { '.js': 'js', '.css': 'css' },
  define: { 'process.env.NODE_ENV': '"production"' },
  minify: false,    // keep test build unminified for debugging
  sourcemap: true,
  treeShaking: true,
  legalComments: 'none'
};

async function build() {
  console.log('🚀 Starting editor build...');

  try {
    // build in parallel
    await Promise.all([
      esbuild.build(stableConfig),
    ]);

    console.log('✅ Build succeeded!');
    console.log(`📦 Stable build: ${stableConfig.outfile} (${(fs.statSync(stableConfig.outfile).size / 1024).toFixed(2)} KB)`);

    const buildInfo = {
      timestamp: new Date().toISOString(),
      version: require('./package.json').version,
    };
    fs.writeFileSync('assets/build-info.json', JSON.stringify(buildInfo, null, 2));
    console.log('📝 Build metadata saved to assets/build-info.json');

  } catch (error) {
    console.error('❌ Build failed:', error.message);
    if (error.errors) {
      error.errors.forEach(err => console.error('   ', err.text));
    }
    process.exit(1);
  }
}

async function watch() {
  console.log('👀 Entering development mode, watching for file changes...');
  try {
    // watch both contexts
    const [stableCtx, testCtx] = await Promise.all([
      esbuild.context(stableConfig),
      esbuild.context(testConfig)
    ]);
    await Promise.all([stableCtx.watch(), testCtx.watch()]);
    console.log('✅ Watch mode started (stable + test)');
  } catch (error) {
    console.error('❌ Watch mode failed:', error);
    process.exit(1);
  }
}

if (process.argv.includes('--watch')) {
  watch();
} else {
  build();
}
