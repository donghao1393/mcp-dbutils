#!/usr/bin/env fish

function sonar-ai-fix
    # 检查当前目录是否是项目目录
    if not test -f "pyproject.toml"; or not test -d "src/mcp_dbutils"
        echo "错误: 请在项目根目录运行此命令"
        echo "当前目录不是mcp-dbutils项目目录"
        return 1
    end
    
    # 下载最新的构件
    echo "正在下载 SonarCloud 分析报告..."
    
    # 获取最新的工作流运行ID
    set RUN_ID (gh run list --workflow "Quality Assurance" --limit 1 --json databaseId --jq '.[0].databaseId')
    
    if test -z "$RUN_ID"
        echo "错误: 无法获取最新的工作流运行ID"
        return 1
    end
    
    # 创建临时目录存放下载的文件
    set TEMP_DIR (mktemp -d)
    
    # 下载构件
    gh run download $RUN_ID --name sonarcloud-issues --dir $TEMP_DIR
    
    if test $status -ne 0
        echo "错误: 下载构件失败"
        rm -rf $TEMP_DIR
        return 1
    end
    
    # 检查文件是否存在
    if not test -f "$TEMP_DIR/sonar_report.md"
        echo "错误: 未找到 sonar_report.md 文件"
        rm -rf $TEMP_DIR
        return 1
    end
    
    if not test -f "$TEMP_DIR/sonar_issues.json"
        echo "错误: 未找到 sonar_issues.json 文件"
        rm -rf $TEMP_DIR
        return 1
    end
    
    # 复制文件到当前目录
    cp "$TEMP_DIR/sonar_report.md" ./sonar_report.md
    cp "$TEMP_DIR/sonar_issues.json" ./sonar_issues.json
    
    # 清理临时目录
    rm -rf $TEMP_DIR
    
    echo "已下载 SonarCloud 分析报告:"
    echo "- sonar_report.md: Markdown格式的报告，适合人类阅读"
    echo "- sonar_issues.json: JSON格式的原始数据，适合AI处理"
    echo ""
    echo "使用方法:"
    echo "1. 查看报告: cat sonar_report.md"
    echo "2. 提供给AI: 将sonar_report.md的内容复制给AI，请求修复建议"
    echo "3. 高级分析: 将sonar_issues.json提供给AI进行更深入的分析"
end
