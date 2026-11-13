# Euler & Heun ODE Laboratory

A complete educational web application for **Unit 3, Session 14: Ordinary Differential Equations**, Numerical Analysis, Systems Engineering, Universidad Peruana Unión (UPeU).

The Spanish-language interface explains every numerical step, compares both methods with the analytic solution, and plots all three trajectories. Python implements the algorithms directly; Flask exposes JSON and serves HTML, CSS, vanilla JavaScript, and Canvas. There are no external fonts, CDNs, JavaScript frameworks, numerical solver libraries, or database requirements.

## Academic scope

The provided learning assignment (`TareaMetodos.pdf`, page 2) asks students to approximate `y(1.2)` manually using Euler and improved Euler with `h=0.1`, compare relative errors with the true value, and develop software. The theoretical guide (`GuiaTeorica Metodos.pdf`, pages 24–26) defines improved Euler as the Heun predictor-corrector method, with one correction.

The handwritten solution and this application are separate deliverables. Editable parameters, Canvas interaction, copying calculations, API validation, automated tests, and deployment preparation are project requirements supplied by the student, not additional professor requirements. The supplied PDFs are not redistributed in this repository.

## Mathematical model

```text
(y² - x²) dx + xy dy = 0
y(1) = 2
y' = f(x,y) = x/y - y/x,  x != 0, y != 0
x0 = 1, y0 = 2, x_final = 1.2, h = 0.1 -> 2 steps
```

**Euler**

```text
y[i+1] = y[i] + h*f(x[i], y[i])
```

**Heun (improved Euler, not midpoint RK2)**

```text
k1 = f(x[i], y[i])
z  = y[i] + h*k1
k2 = f(x[i+1], z)
y[i+1] = y[i] + h*(k1+k2)/2
```

Implementation averages as `k1/2 + k2/2` to avoid an unnecessary overflow when adding large slopes. No intermediate rounding is performed. Nodes are computed from the starting point and iteration index to avoid cumulative addition drift; the last node is labeled with the requested endpoint after validating the fixed-step grid.

**Analytic solution**

Setting `u=y²` yields `u' + 2u/x = 2x`. Multiplying by `x²` and integrating gives `x²u = x⁴/2 + C`:

```text
C = x0²*y0² - x0⁴/2
y(x) = sign(y0) * sqrt(x²/2 + C/x²)
```

The initial sign is retained, including negative initial conditions. For the official problem, `C=3.5` and the positive branch is used.

```text
absolute error = abs(exact - approximate)
relative percentage error = absolute error / abs(exact) * 100
```

## Computed reference results

Exact `y(1.2) = 1.7749804380768697`.

| Method | Approximation | Absolute error | Relative error (%) |
| --- | ---: | ---: | ---: |
| Euler | 1.7412776412776414 | 0.033702796799228274 | 1.8987700414177011 |
| Heun | 1.775806670950786 | 0.000826232873916366 | 0.04654884393044697 |

| Step | Euler y next | Heun predictor | Heun corrector |
| --- | ---: | ---: | ---: |
| 1 | 1.85 | 1.85 | 1.8706388206388207 |
| 2 | 1.7412776412776414 | 1.759384187290956 | 1.775806670950786 |

Heun has the smaller error in this experiment. This is not a promise that Heun always has the smaller error for every possible input. IEEE-754 arithmetic can produce differences in the last digits depending on expression evaluation order; assertions use tolerances.

## Architecture

```text
backend/
  __init__.py
  app.py                    # App factory, local entry point, HTTP validation
  serve.py                  # Waitress entry point for Render
  templates/index.html      # Spanish academic interface
  static/css/styles.css     # Responsive visual design
  static/js/app.js           # Forms, rendering, clipboard and Canvas
metodos/
  __init__.py
  euler.py                  # Independent explicit Euler recurrence
  heun.py                   # Independent predictor-corrector recurrence
  problema_pvi.py            # Slope, exact solution, errors, orchestration
  validaciones.py            # Parameter and floating-point validation
tests/
  test_euler.py
  test_heun.py
  test_problema.py
  test_validaciones.py
  test_app.py
docs/
  VERIFICACION.md            # Verification and delivery record in Spanish
  desktop.jpg               # Verified desktop screenshot
  mobile.jpg                # Verified mobile screenshot
README.md
requirements.txt
render.yaml
.python-version
.gitignore
```

Both numerical methods accept a callable slope function and validated `Parametros`. The HTTP boundary validates the official problem's domain. This separation permits testing the recurrences against unrelated differential equations with independently known answers.

## Installation (Windows / PowerShell)

Open a terminal **inside this project's directory**. Python 3.13.17 is the verified version.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Using the environment executable directly avoids PowerShell activation-policy requirements. Packages are installed in `.venv`, not globally. The two direct dependencies are Flask and Waitress; `unittest`, `decimal`, and `fractions` belong to the standard library.

## Run locally

```powershell
.\.venv\Scripts\python.exe -m backend.app
```

Open [http://127.0.0.1:5014](http://127.0.0.1:5014). Press `Ctrl+C` in the terminal to stop. The local development entry point binds only to loopback and disables debug mode.

To choose a different local port:

```powershell
$env:PORT = '5015'
.\.venv\Scripts\python.exe -m backend.app
```

For a local production-server smoke test:

```powershell
.\.venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=5015 backend.app:app
```

## Demonstration workflow

1. Open the app: the official case is calculated automatically.
2. Compare the exact value, Euler and Heun cards.
3. Toggle chart series and move the pointer over the plot to inspect numerical nodes.
4. Select iteration 1 or 2 to show numerical substitution, predictor and corrector.
5. Read full iteration tables and absolute/relative errors. Tables paginate after 20 rows; every row remains available.
6. Choose **Copiar cálculos** for a report with all intermediate values. If the clipboard is denied, the report downloads as UTF-8 text.
7. Change `y0` to `-2` or reduce `h` to explore another case. Changed inputs display a stale-results notice until recalculation.
8. Choose **Restaurar ejercicio** to return to the official problem and recalculate.

Display formatting uses up to 13 significant digits, while the API and copied report retain the full float values. Decimal points are used consistently in the inputs and equations.

## Validation and supported scope

- Numeric finite JSON values only: booleans, strings, null, missing or unknown fields are rejected.
- Forward integration with `x_final > x0`, `h > 0`, and 1–10,000 fixed steps.
- Integer-step tolerance: `math.isclose(n, round(n), rel_tol=1e-12, abs_tol=1e-9)`.
- `x0`, `x_final`, and `y0` must be nonzero. Intervals crossing `x=0` are rejected.
- Exact-reference radicand must remain strictly positive. Since `x` retains its sign, endpoint positivity of `x⁴/2+C` proves positivity throughout the interval.
- Numerical stages, predictors and final values must remain finite and on the initial `y` branch. A coarse step crossing `y=0` is rejected with an instruction to reduce `h`.
- Extreme scales that overflow, underflow the squared denominator, or cannot represent distinct nodes are rejected. This is finite-precision educational software, not an arbitrary-precision solver.
- No backward integration, variable step, arbitrary expression evaluation, RK3 or RK4 is included.

## HTTP API

`POST /api/resolver`, with `Content-Type: application/json`:

```json
{"x0": 1, "y0": 2, "x_final": 1.2, "h": 0.1}
```

Successful response (`200`): `estado`, `parametros` (including `pasos`), `constante`, `valor_exacto`, `euler`, `heun`, `mas_preciso`, and `grafica`.

Each method contains `valor`, `traza`, `puntos`, and `errores`. Each trace row includes the current point, step, first slope, increment and next point; Heun additionally returns `predictor` and `k2`. `grafica.exacta` contains 301 analytic samples, while numerical series contain all computed nodes.

Errors return `{"estado":"error","mensaje":"..."}` with `400` for invalid input/domain or malformed JSON, `413` for bodies over 16 KiB, and `415` for incorrect content type. Incorrect API methods return JSON `405`. `GET /health` returns `{"estado":"ok"}`.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q backend metodos tests
node --check backend/static/js/app.js
.\.venv\Scripts\python.exe -m pip check
```

The suite covers official results and traces, negative conditions, invalid domains, finite arithmetic, HTTP and static resources. Independent checks include exact fractions, 60-digit Decimal calculations, a conserved quantity, derivative consistency, analytic integrals, stability polynomials and measured convergence orders. A nonlinear test distinguishes Heun from the midpoint method.

See [the verification record](docs/VERIFICACION.md) for executed checks, browser coverage and limitations. No remote repository or Render service has been created.

Latest verification: **75 tests passed** with Python 3.13.17. The Blueprint passed validation against Render's official JSON Schema.

![Desktop results and comparison chart](docs/desktop.jpg)

[Mobile screenshot](docs/mobile.jpg)

## Future Render deployment

`render.yaml` is a prepared single-service Blueprint with `python -m backend.serve`, a `/health` check, free compute, and automatic deployment disabled. `.python-version` pins Python 3.13.17. Waitress binds to `0.0.0.0` and Render's `PORT`; no local development server is used in production.

After explicit publication approval, use a **new independent repository**, suggested name `numerical-methods-euler-heun-ode`, with this project directory as its root. Do not publish into the composite-trapezoidal-rule repository. Review the available plan and run platform-side Blueprint validation before creating any service. Free-plan availability and limits may change.

Configuration references: [Render Blueprint specification](https://render.com/docs/blueprint-spec), [Python version selection](https://render.com/docs/python-version), [Flask installation and environments](https://flask.palletsprojects.com/en/stable/installation/).