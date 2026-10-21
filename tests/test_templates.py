from pathlib import Path
import re


def test_all_templates_compile_and_post_forms_have_csrf():
    import main
    for filename in main.app.jinja_env.list_templates():
        main.app.jinja_env.get_template(filename)
        source = (Path(main.app.template_folder) / filename).read_text(encoding='utf-8')
        for form in re.findall(r'<form\b.*?</form>', source, flags=re.S | re.I):
            opening = form.split('>', 1)[0]
            if re.search(r'''method\s*=\s*['"]post['"]''', opening, re.I):
                assert 'name="csrf_token"' in form, filename
