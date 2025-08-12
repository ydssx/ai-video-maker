#!/usr/bin/env node
/**
 * 检查前端组件的导入问题
 */

const fs = require('fs');
const path = require('path');

function checkFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const issues = [];
  
  // 检查常见的导入问题
  const commonIssues = [
    {
      pattern: /message\.(success|error|warning|info)/g,
      import: 'message',
      from: 'antd'
    },
    {
      pattern: /notification\.(success|error|warning|info)/g,
      import: 'notification',
      from: 'antd'
    },
    {
      pattern: /Modal\.(confirm|info|success|error|warning)/g,
      import: 'Modal',
      from: 'antd'
    }
  ];
  
  commonIssues.forEach(issue => {
    const matches = content.match(issue.pattern);
    if (matches) {
      // 检查是否已导入
      const importRegex = new RegExp(`import.*{[^}]*${issue.import}[^}]*}.*from\\s+['"]${issue.from}['"]`);
      if (!importRegex.test(content)) {
        issues.push(`缺少导入: ${issue.import} from '${issue.from}'`);
      }
    }
  });
  
  return issues;
}

function checkDirectory(dir) {
  const files = fs.readdirSync(dir);
  const allIssues = {};
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      const subIssues = checkDirectory(filePath);
      Object.assign(allIssues, subIssues);
    } else if (file.endsWith('.js') || file.endsWith('.jsx')) {
      const issues = checkFile(filePath);
      if (issues.length > 0) {
        allIssues[filePath] = issues;
      }
    }
  });
  
  return allIssues;
}

function main() {
  console.log('=== 前端导入检查工具 ===\n');
  
  const frontendDir = path.join(__dirname, 'frontend', 'src');
  
  if (!fs.existsSync(frontendDir)) {
    console.log('❌ 前端源码目录不存在');
    return;
  }
  
  const issues = checkDirectory(frontendDir);
  
  if (Object.keys(issues).length === 0) {
    console.log('✅ 没有发现导入问题');
  } else {
    console.log('发现以下导入问题:\n');
    
    Object.entries(issues).forEach(([file, fileIssues]) => {
      console.log(`📁 ${file}:`);
      fileIssues.forEach(issue => {
        console.log(`  ❌ ${issue}`);
      });
      console.log();
    });
  }
  
  console.log('检查完成！');
}

if (require.main === module) {
  main();
}