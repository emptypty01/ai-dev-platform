# 仅本机首次初始化使用；输出文件不打印 Token。
user = User.find_by_username!('root')
token = user.personal_access_tokens.create!(name: 'local-platform-bootstrap', scopes: ['api'], expires_at: 7.days.from_now)
File.write('/tmp/local-platform-bootstrap-token', token.token)
File.chmod(0600, '/tmp/local-platform-bootstrap-token')
puts 'Bootstrap token created in restricted temporary file'
