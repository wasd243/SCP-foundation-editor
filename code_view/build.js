// build.js - 修复别名错误版
const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

const assetsDir = path.join(__dirname, 'assets');
if (!fs.existsSync(assetsDir)) {
  fs.mkdirSync(assetsDir, { recursive: true });
}

// 稳定版配置（不动）
const stableConfig = {
  entryPoints: ['editor.js'],
  bundle: true,
  outfile: 'assets/bundle_editor.js',
  format: 'esm',
  platform: 'browser',
  target: ['es2020'],
  loader: { '.js': 'js', '.css': 'css' },
  define: { 'process.env.NODE_ENV': '"production"' },
  minify: true,
  sourcemap: true,
  treeShaking: true,
  legalComments: 'none'
};

//（lezer版）
const testConfig = {
  entryPoints: ['editor.js'],
  bundle: true,
  outfile: 'assets/bundle_editor.js',
  format: 'esm',
  platform: 'browser',
  target: ['es2020'],
  loader: { '.js': 'js', '.css': 'css' },
  define: { 'process.env.NODE_ENV': '"production"' },
  minify: false,    // 测试版不压缩，方便调试
  sourcemap: true,
  treeShaking: true,
  legalComments: 'none'
};

async function build() {
  console.log('🚀 开始构建编辑器...');

  try {
    // 同时构建两个
    await Promise.all([
      esbuild.build(stableConfig),
      esbuild.build(testConfig)
    ]);

    console.log('✅ 构建成功!');
    console.log(`📦 稳定版: ${stableConfig.outfile} (${(fs.statSync(stableConfig.outfile).size / 1024).toFixed(2)} KB)`);
    console.log(`📦 测试版: ${testConfig.outfile} (${(fs.statSync(testConfig.outfile).size / 1024).toFixed(2)} KB)`);

    const buildInfo = {
      timestamp: new Date().toISOString(),
      version: require('./package.json').version,
    };
    fs.writeFileSync('assets/build-info.json', JSON.stringify(buildInfo, null, 2));
    console.log('📝 构建信息已保存到 assets/build-info.json');

  } catch (error) {
    console.error('❌ 构建失败:', error.message);
    if (error.errors) {
      error.errors.forEach(err => console.error('   ', err.text));
    }
    process.exit(1);
  }
}

async function watch() {
  console.log('👀 进入开发模式，监听文件变化...');
  try {
    // 两个都监听
    const [stableCtx, testCtx] = await Promise.all([
      esbuild.context(stableConfig),
      esbuild.context(testConfig)
    ]);
    await Promise.all([stableCtx.watch(), testCtx.watch()]);
    console.log('✅ 监听已启动（稳定版 + 测试版）');
  } catch (error) {
    console.error('❌ 监听失败:', error);
    process.exit(1);
  }
}

if (process.argv.includes('--watch')) {
  watch();
} else {
  build();
}