import { i as __toESM } from "../_runtime.mjs";
import { K as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as ScanSearch } from "../_libs/lucide-react.mjs";
import { a as ResponsiveContainer, i as Bar, n as YAxis, o as Tooltip, r as XAxis, t as BarChart } from "../_libs/recharts+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-CJZNyNwB.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var scoreboard_default = {
	benchmark: {
		"name": "ShadowBench",
		"version": "1.0.0",
		"seed": "shadowbench-450-v1",
		"cases": 450,
		"surfaces": [
			"code",
			"identity",
			"gateway",
			"lowcode",
			"saas",
			"cloud",
			"endpoint",
			"network",
			"runtime"
		],
		"per_surface": {
			"code": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"identity": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"gateway": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"lowcode": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"saas": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"cloud": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"endpoint": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"network": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			},
			"runtime": {
				"positive": 25,
				"negative": 15,
				"near_miss": 10
			}
		},
		"formats": {
			"code": "Minimal application tree (Python or Node, plus optional agent config).",
			"identity": "Okta GET /api/v1/apps JSON export, status ACTIVE.",
			"gateway": "LiteLLM-style JSONL spend log (one record).",
			"lowcode": "n8n workflow export JSON (id, name, nodes, connections).",
			"saas": "Slack admin approved-app record JSON, with workspace id.",
			"cloud": "JSONL record in the AWS inventory dump shape (agent or lambda).",
			"endpoint": "Linux home-directory fragment with vendor config paths.",
			"network": "JSONL DNS log row with src_ip, query and ts.",
			"runtime": "osquery processes JSON array (name, path, cmdline, pid)."
		},
		"provenance": "synthetic-realistic",
		"corpus_sha256": "a874ddcf2c1bbb62746f9830798db1d3e96148ae26b71304f217bf4025392be3",
		"label_rule": "Labels are the planted facts in truth.json. No evaluated tool produced them."
	},
	smoke: false,
	scored_cases: 450,
	tools: [
		{
			"id": "shadowscan",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "shadowscan, version 0.1.2",
			"applicable_surfaces": [
				"cloud",
				"code",
				"endpoint",
				"gateway",
				"identity",
				"lowcode",
				"network",
				"runtime",
				"saas"
			],
			"metrics": {
				"quality": {
					"cases_scored": 450,
					"errors": 0,
					"fact": {
						"tp": 295,
						"fp": 82,
						"fn": 41,
						"precision": .7824933687002652,
						"recall": .8779761904761905,
						"f1": .8274894810659186
					},
					"case": {
						"tp": 203,
						"fp": 6,
						"tn": 219,
						"fn": 22,
						"precision": .9712918660287081,
						"recall": .9022222222222223,
						"specificity": .9733333333333334,
						"fpr": .026666666666666616,
						"balanced_accuracy": .9377777777777778,
						"mcc": .8777777372889612
					},
					"by_surface": {
						"cloud": {
							"tp": 65,
							"fp": 0,
							"fn": 0,
							"precision": 1,
							"recall": 1,
							"f1": 1,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"code": {
							"tp": 26,
							"fp": 4,
							"fn": 2,
							"precision": .8666666666666667,
							"recall": .9285714285714286,
							"f1": .896551724137931,
							"case_tp": 23,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 2
						},
						"endpoint": {
							"tp": 40,
							"fp": 5,
							"fn": 8,
							"precision": .8888888888888888,
							"recall": .8333333333333334,
							"f1": .8602150537634408,
							"case_tp": 21,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 4
						},
						"gateway": {
							"tp": 25,
							"fp": 3,
							"fn": 0,
							"precision": .8928571428571429,
							"recall": 1,
							"f1": .9433962264150945,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"identity": {
							"tp": 19,
							"fp": 32,
							"fn": 6,
							"precision": .37254901960784315,
							"recall": .76,
							"f1": .5,
							"case_tp": 19,
							"case_fp": 3,
							"case_tn": 22,
							"case_fn": 6
						},
						"lowcode": {
							"tp": 55,
							"fp": 0,
							"fn": 15,
							"precision": 1,
							"recall": .7857142857142857,
							"f1": .88,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"network": {
							"tp": 25,
							"fp": 0,
							"fn": 0,
							"precision": 1,
							"recall": 1,
							"f1": 1,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"runtime": {
							"tp": 16,
							"fp": 6,
							"fn": 9,
							"precision": .7272727272727273,
							"recall": .64,
							"f1": .6808510638297872,
							"case_tp": 16,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 9
						},
						"saas": {
							"tp": 24,
							"fp": 32,
							"fn": 1,
							"precision": .42857142857142855,
							"recall": .96,
							"f1": .5925925925925924,
							"case_tp": 24,
							"case_fp": 3,
							"case_tn": 22,
							"case_fn": 1
						}
					},
					"fact_f1_ci95": [.7857142857142857, .8633879781420765]
				},
				"estate_recall": .8779761904761905,
				"estate_fact_fn": 41,
				"estate_fact_tp": 295
			},
			"latency_ms": {
				"n": 450,
				"p50": 1128,
				"p95": 1224
			}
		},
		{
			"id": "vet",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "1.20.0",
			"applicable_surfaces": ["code", "endpoint"],
			"metrics": {
				"quality": {
					"cases_scored": 98,
					"errors": 2,
					"fact": {
						"tp": 22,
						"fp": 4,
						"fn": 52,
						"precision": .8461538461538461,
						"recall": .2972972972972973,
						"f1": .44000000000000006
					},
					"case": {
						"tp": 15,
						"fp": 0,
						"tn": 49,
						"fn": 34,
						"precision": 1,
						"recall": .30612244897959184,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .653061224489796,
						"mcc": .4251151509488518
					},
					"by_surface": {
						"code": {
							"tp": 8,
							"fp": 4,
							"fn": 20,
							"precision": .6666666666666666,
							"recall": .2857142857142857,
							"f1": .4,
							"case_tp": 8,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 17
						},
						"endpoint": {
							"tp": 14,
							"fp": 0,
							"fn": 32,
							"precision": 1,
							"recall": .30434782608695654,
							"f1": .4666666666666667,
							"case_tp": 7,
							"case_fp": 0,
							"case_tn": 24,
							"case_fn": 17
						}
					},
					"fact_f1_ci95": [.2857142857142857, .5813953488372092]
				},
				"estate_recall": .06547619047619048,
				"estate_fact_fn": 314,
				"estate_fact_tp": 22
			},
			"latency_ms": {
				"n": 100,
				"p50": 432,
				"p95": 480
			}
		},
		{
			"id": "numbat",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "numbat 0.2.0 (schema 0.3.0)",
			"applicable_surfaces": ["endpoint"],
			"metrics": {
				"quality": {
					"cases_scored": 50,
					"errors": 0,
					"fact": {
						"tp": 0,
						"fp": 0,
						"fn": 48,
						"precision": null,
						"recall": 0,
						"f1": 0
					},
					"case": {
						"tp": 0,
						"fp": 0,
						"tn": 25,
						"fn": 25,
						"precision": null,
						"recall": 0,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .5,
						"mcc": null
					},
					"by_surface": { "endpoint": {
						"tp": 0,
						"fp": 0,
						"fn": 48,
						"precision": null,
						"recall": 0,
						"f1": 0,
						"case_tp": 0,
						"case_fp": 0,
						"case_tn": 25,
						"case_fn": 25
					} },
					"fact_f1_ci95": [0, 0]
				},
				"estate_recall": 0,
				"estate_fact_fn": 336,
				"estate_fact_tp": 0
			},
			"latency_ms": {
				"n": 50,
				"p50": 118,
				"p95": 135
			}
		},
		{
			"id": "snyk-agent-scan",
			"role": "tool",
			"status": "not_run",
			"status_detail": "not run: scan refused without a Snyk token",
			"version": null,
			"applicable_surfaces": ["endpoint"]
		},
		{
			"id": "ai-bom",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "ai-bom version 3.6.0",
			"applicable_surfaces": ["code", "lowcode"],
			"metrics": {
				"quality": {
					"cases_scored": 100,
					"errors": 0,
					"fact": {
						"tp": 13,
						"fp": 2,
						"fn": 85,
						"precision": .8666666666666667,
						"recall": .1326530612244898,
						"f1": .23008849557522126
					},
					"case": {
						"tp": 13,
						"fp": 0,
						"tn": 50,
						"fn": 37,
						"precision": 1,
						"recall": .26,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .63,
						"mcc": .38655567174253413
					},
					"by_surface": {
						"code": {
							"tp": 13,
							"fp": 2,
							"fn": 15,
							"precision": .8666666666666667,
							"recall": .4642857142857143,
							"f1": .6046511627906976,
							"case_tp": 13,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 12
						},
						"lowcode": {
							"tp": 0,
							"fp": 0,
							"fn": 70,
							"precision": null,
							"recall": 0,
							"f1": 0,
							"case_tp": 0,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 25
						}
					},
					"fact_f1_ci95": [.12280701754385964, .3418803418803419]
				},
				"estate_recall": .03869047619047619,
				"estate_fact_fn": 323,
				"estate_fact_tp": 13
			},
			"latency_ms": {
				"n": 100,
				"p50": 267,
				"p95": 282
			}
		},
		{
			"id": "nuguard",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "0.9.15",
			"applicable_surfaces": ["code"],
			"metrics": {
				"quality": {
					"cases_scored": 50,
					"errors": 0,
					"fact": {
						"tp": 19,
						"fp": 4,
						"fn": 9,
						"precision": .8260869565217391,
						"recall": .6785714285714286,
						"f1": .7450980392156864
					},
					"case": {
						"tp": 18,
						"fp": 1,
						"tn": 24,
						"fn": 7,
						"precision": .9473684210526315,
						"recall": .72,
						"specificity": .96,
						"fpr": .040000000000000036,
						"balanced_accuracy": .84,
						"mcc": .7004727969157798
					},
					"by_surface": { "code": {
						"tp": 19,
						"fp": 4,
						"fn": 9,
						"precision": .8260869565217391,
						"recall": .6785714285714286,
						"f1": .7450980392156864,
						"case_tp": 18,
						"case_fp": 1,
						"case_tn": 24,
						"case_fn": 7
					} },
					"fact_f1_ci95": [.5957446808510638, .8571428571428572]
				},
				"estate_recall": .05654761904761905,
				"estate_fact_fn": 317,
				"estate_fact_tp": 19
			},
			"latency_ms": {
				"n": 50,
				"p50": 1724,
				"p95": 1873
			}
		},
		{
			"id": "agentdiscover",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "AgentDiscover v2.9.5",
			"applicable_surfaces": ["code"],
			"metrics": {
				"quality": {
					"cases_scored": 50,
					"errors": 0,
					"fact": {
						"tp": 5,
						"fp": 0,
						"fn": 23,
						"precision": 1,
						"recall": .17857142857142858,
						"f1": .30303030303030304
					},
					"case": {
						"tp": 4,
						"fp": 0,
						"tn": 25,
						"fn": 21,
						"precision": 1,
						"recall": .16,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .58,
						"mcc": .29488391230979427
					},
					"by_surface": { "code": {
						"tp": 5,
						"fp": 0,
						"fn": 23,
						"precision": 1,
						"recall": .17857142857142858,
						"f1": .30303030303030304,
						"case_tp": 4,
						"case_fp": 0,
						"case_tn": 25,
						"case_fn": 21
					} },
					"fact_f1_ci95": [.07407407407407407, .5294117647058824]
				},
				"estate_recall": .01488095238095238,
				"estate_fact_fn": 331,
				"estate_fact_tp": 5
			},
			"latency_ms": {
				"n": 50,
				"p50": 807,
				"p95": 850
			}
		},
		{
			"id": "agentic-radar",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": "0.14.1",
			"applicable_surfaces": ["code", "lowcode"],
			"metrics": {
				"quality": {
					"cases_scored": 100,
					"errors": 0,
					"fact": {
						"tp": 0,
						"fp": 0,
						"fn": 98,
						"precision": null,
						"recall": 0,
						"f1": 0
					},
					"case": {
						"tp": 0,
						"fp": 0,
						"tn": 50,
						"fn": 50,
						"precision": null,
						"recall": 0,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .5,
						"mcc": null
					},
					"by_surface": {
						"code": {
							"tp": 0,
							"fp": 0,
							"fn": 28,
							"precision": null,
							"recall": 0,
							"f1": 0,
							"case_tp": 0,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 25
						},
						"lowcode": {
							"tp": 0,
							"fp": 0,
							"fn": 70,
							"precision": null,
							"recall": 0,
							"f1": 0,
							"case_tp": 0,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 25
						}
					},
					"fact_f1_ci95": [0, 0]
				},
				"estate_recall": 0,
				"estate_fact_fn": 336,
				"estate_fact_tp": 0
			},
			"latency_ms": {
				"n": 100,
				"p50": 4194,
				"p95": 4325
			}
		},
		{
			"id": "aiostack",
			"role": "tool",
			"status": "not_run",
			"status_detail": "not run: AIOstack is a Kubernetes daemon with no offline fixture mode in this environment",
			"version": null,
			"applicable_surfaces": ["runtime"]
		},
		{
			"id": "curatedmcp",
			"role": "tool",
			"status": "scored",
			"status_detail": "run",
			"version": null,
			"applicable_surfaces": ["endpoint"],
			"metrics": {
				"quality": {
					"cases_scored": 50,
					"errors": 0,
					"fact": {
						"tp": 18,
						"fp": 0,
						"fn": 30,
						"precision": 1,
						"recall": .375,
						"f1": .5454545454545454
					},
					"case": {
						"tp": 9,
						"fp": 0,
						"tn": 25,
						"fn": 16,
						"precision": 1,
						"recall": .36,
						"specificity": 1,
						"fpr": 0,
						"balanced_accuracy": .6799999999999999,
						"mcc": .4685212856658182
					},
					"by_surface": { "endpoint": {
						"tp": 18,
						"fp": 0,
						"fn": 30,
						"precision": 1,
						"recall": .375,
						"f1": .5454545454545454,
						"case_tp": 9,
						"case_fp": 0,
						"case_tn": 25,
						"case_fn": 16
					} },
					"fact_f1_ci95": [.3018867924528302, .7228915662650602]
				},
				"estate_recall": .05357142857142857,
				"estate_fact_fn": 318,
				"estate_fact_tp": 18
			},
			"latency_ms": {
				"n": 50,
				"p50": 6758,
				"p95": 8143
			}
		},
		{
			"id": "reference-lexicon",
			"role": "reference",
			"status": "scored",
			"status_detail": "run",
			"version": null,
			"applicable_surfaces": [
				"cloud",
				"code",
				"endpoint",
				"gateway",
				"identity",
				"lowcode",
				"network",
				"runtime",
				"saas"
			],
			"metrics": {
				"quality": {
					"cases_scored": 450,
					"errors": 0,
					"fact": {
						"tp": 290,
						"fp": 42,
						"fn": 46,
						"precision": .8734939759036144,
						"recall": .8630952380952381,
						"f1": .8682634730538922
					},
					"case": {
						"tp": 222,
						"fp": 8,
						"tn": 217,
						"fn": 3,
						"precision": .9652173913043478,
						"recall": .9866666666666667,
						"specificity": .9644444444444444,
						"fpr": .03555555555555556,
						"balanced_accuracy": .9755555555555555,
						"mcc": .9513460403751882
					},
					"by_surface": {
						"cloud": {
							"tp": 40,
							"fp": 0,
							"fn": 25,
							"precision": 1,
							"recall": .6153846153846154,
							"f1": .761904761904762,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"code": {
							"tp": 26,
							"fp": 3,
							"fn": 2,
							"precision": .896551724137931,
							"recall": .9285714285714286,
							"f1": .912280701754386,
							"case_tp": 24,
							"case_fp": 1,
							"case_tn": 24,
							"case_fn": 1
						},
						"endpoint": {
							"tp": 46,
							"fp": 22,
							"fn": 2,
							"precision": .6764705882352942,
							"recall": .9583333333333334,
							"f1": .7931034482758621,
							"case_tp": 25,
							"case_fp": 1,
							"case_tn": 24,
							"case_fn": 0
						},
						"gateway": {
							"tp": 25,
							"fp": 3,
							"fn": 0,
							"precision": .8928571428571429,
							"recall": 1,
							"f1": .9433962264150945,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"identity": {
							"tp": 24,
							"fp": 6,
							"fn": 1,
							"precision": .8,
							"recall": .96,
							"f1": .8727272727272728,
							"case_tp": 24,
							"case_fp": 3,
							"case_tn": 22,
							"case_fn": 1
						},
						"lowcode": {
							"tp": 55,
							"fp": 0,
							"fn": 15,
							"precision": 1,
							"recall": .7857142857142857,
							"f1": .88,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"network": {
							"tp": 25,
							"fp": 0,
							"fn": 0,
							"precision": 1,
							"recall": 1,
							"f1": 1,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"runtime": {
							"tp": 25,
							"fp": 3,
							"fn": 0,
							"precision": .8928571428571429,
							"recall": 1,
							"f1": .9433962264150945,
							"case_tp": 25,
							"case_fp": 0,
							"case_tn": 25,
							"case_fn": 0
						},
						"saas": {
							"tp": 24,
							"fp": 5,
							"fn": 1,
							"precision": .8275862068965517,
							"recall": .96,
							"f1": .888888888888889,
							"case_tp": 24,
							"case_fp": 3,
							"case_tn": 22,
							"case_fn": 1
						}
					},
					"fact_f1_ci95": [.8257142857142857, .9068702290076336]
				},
				"estate_recall": .8630952380952381,
				"estate_fact_fn": 46,
				"estate_fact_tp": 290
			},
			"latency_ms": {
				"n": 0,
				"p50": null,
				"p95": null
			}
		}
	],
	methodology: {
		"positives_per_surface": 25,
		"negatives_per_surface": 15,
		"near_misses_per_surface": 10,
		"primary_metric": "Fact-level precision, recall and F1 on surfaces the tool can read.",
		"estate_recall": "Positive facts on surfaces the tool cannot read count as misses. Unscanned negatives are not counted as true negatives.",
		"case_metric": "A positive case is detected when any planted fact is returned. Any mapped finding on a negative or near-miss case is a false positive.",
		"errors": "Timeouts and crashes are excluded from precision and recall and reported separately.",
		"reference": "reference-lexicon applies the published alias table to the artifact text. It is a string-match ceiling, not a product."
	}
};
var cases_default = /*#__PURE__*/ JSON.parse("[{\"id\":\"cloud-001\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-000\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-000\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"aws.jsonl\",\"quote\":\"anthropic.claude-3-sonnet-20240229-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-002\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-001\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-001\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-003\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-002\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-002\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-004\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-003\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-003\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"aws.jsonl\",\"quote\":\"mistral.mistral-large-2402-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-005\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-004\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-004\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"aws.jsonl\",\"quote\":\"cohere.command-r-plus-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-006\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-005\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-005\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"aws.jsonl\",\"quote\":\"anthropic.claude-3-sonnet-20240229-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-007\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-006\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-006\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-008\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-007\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-007\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-009\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-008\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-008\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"aws.jsonl\",\"quote\":\"mistral.mistral-large-2402-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-010\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-009\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-009\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"aws.jsonl\",\"quote\":\"cohere.command-r-plus-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-011\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-010\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-010\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"aws.jsonl\",\"quote\":\"anthropic.claude-3-sonnet-20240229-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-012\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-011\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-011\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-013\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-012\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-012\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-014\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-013\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-013\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"aws.jsonl\",\"quote\":\"mistral.mistral-large-2402-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-015\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-014\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-014\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"aws.jsonl\",\"quote\":\"cohere.command-r-plus-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-016\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-015\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-015\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"aws.jsonl\",\"quote\":\"anthropic.claude-3-sonnet-20240229-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-017\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-016\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-016\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-018\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-017\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-017\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-019\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-018\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-018\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"aws.jsonl\",\"quote\":\"mistral.mistral-large-2402-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-020\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-019\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-019\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"aws.jsonl\",\"quote\":\"cohere.command-r-plus-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-021\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-020\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-020\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"aws.jsonl\",\"quote\":\"anthropic.claude-3-sonnet-20240229-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-022\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-021\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-021\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-023\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-022\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-022\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"}],\"forbidden\":[]},{\"id\":\"cloud-024\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-023\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-023\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"aws.jsonl\",\"quote\":\"mistral.mistral-large-2402-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-025\",\"surface\":\"cloud\",\"polarity\":\"positive\",\"title\":\"Bedrock agent agent-024\",\"facts\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\",\"path\":\"aws.jsonl\",\"quote\":\"agent-024\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"aws.jsonl\",\"quote\":\"bedrock\"},{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"aws.jsonl\",\"quote\":\"cohere.command-r-plus-v1:0\"}],\"forbidden\":[]},{\"id\":\"cloud-026\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-25\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-027\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-26\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-028\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-27\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-029\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-28\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-030\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-29\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-031\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-30\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-032\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-31\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-033\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-32\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-034\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-33\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-035\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-34\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-036\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-35\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-037\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-36\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-038\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-37\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-039\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-38\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-040\",\"surface\":\"cloud\",\"polarity\":\"negative\",\"title\":\"Lambda billing-csv-39\",\"facts\":[],\"forbidden\":[]},{\"id\":\"cloud-041\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-042\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-043\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-044\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-045\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-046\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-047\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-048\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-049\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"cloud-050\",\"surface\":\"cloud\",\"polarity\":\"near_miss\",\"title\":\"Lambda that polls a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"code-001\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal openai\",\"facts\":[{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"src/chat.py\",\"quote\":\"from openai import OpenAI\"}],\"forbidden\":[]},{\"id\":\"code-002\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal langchain\",\"facts\":[{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"src/chain.py\",\"quote\":\"from langchain.chat_models import ChatOpenAI\"}],\"forbidden\":[]},{\"id\":\"code-003\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal langgraph\",\"facts\":[{\"category\":\"framework\",\"value\":\"langgraph\",\"path\":\"src/graph.py\",\"quote\":\"from langgraph.graph import StateGraph\"}],\"forbidden\":[]},{\"id\":\"code-004\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal crewai\",\"facts\":[{\"category\":\"framework\",\"value\":\"crewai\",\"path\":\"src/crew.py\",\"quote\":\"from crewai import Agent, Crew\"}],\"forbidden\":[]},{\"id\":\"code-005\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal autogen\",\"facts\":[{\"category\":\"framework\",\"value\":\"autogen\",\"path\":\"src/team.py\",\"quote\":\"from autogen import AssistantAgent\"}],\"forbidden\":[]},{\"id\":\"code-006\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal anthropic\",\"facts\":[{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"src/ask.py\",\"quote\":\"import anthropic\"}],\"forbidden\":[]},{\"id\":\"code-007\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal google-gemini\",\"facts\":[{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"src/gem.py\",\"quote\":\"import google.generativeai as genai\"}],\"forbidden\":[]},{\"id\":\"code-008\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal mcp-github\",\"facts\":[{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\".cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"}],\"forbidden\":[]},{\"id\":\"code-009\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal claude-code\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"CLAUDE.md\",\"quote\":\"filesystem tools already configured\"},{\"category\":\"mcp\",\"value\":\"mcp-filesystem\",\"path\":\".mcp.json\",\"quote\":\"@modelcontextprotocol/server-filesystem\"}],\"forbidden\":[]},{\"id\":\"code-010\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal llamaindex\",\"facts\":[{\"category\":\"framework\",\"value\":\"llamaindex\",\"path\":\"src/idx.py\",\"quote\":\"from llama_index.core import VectorStoreIndex\"}],\"forbidden\":[]},{\"id\":\"code-011\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal dspy\",\"facts\":[{\"category\":\"framework\",\"value\":\"dspy\",\"path\":\"src/opt.py\",\"quote\":\"import dspy\"}],\"forbidden\":[]},{\"id\":\"code-012\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal pydantic-ai\",\"facts\":[{\"category\":\"framework\",\"value\":\"pydantic-ai\",\"path\":\"src/agent.py\",\"quote\":\"from pydantic_ai import Agent\"}],\"forbidden\":[]},{\"id\":\"code-013\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal haystack\",\"facts\":[{\"category\":\"framework\",\"value\":\"haystack\",\"path\":\"src/pipe.py\",\"quote\":\"from haystack import Pipeline\"}],\"forbidden\":[]},{\"id\":\"code-014\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal smolagents\",\"facts\":[{\"category\":\"framework\",\"value\":\"smolagents\",\"path\":\"src/loop.py\",\"quote\":\"from smolagents import CodeAgent\"}],\"forbidden\":[]},{\"id\":\"code-015\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal mistral\",\"facts\":[{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"src/m.py\",\"quote\":\"from mistralai.client import MistralClient\"}],\"forbidden\":[]},{\"id\":\"code-016\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal groq\",\"facts\":[{\"category\":\"provider\",\"value\":\"groq\",\"path\":\"src/g.py\",\"quote\":\"from groq import Groq\"}],\"forbidden\":[]},{\"id\":\"code-017\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal cohere\",\"facts\":[{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"src/c.py\",\"quote\":\"import cohere\"}],\"forbidden\":[]},{\"id\":\"code-018\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal ollama\",\"facts\":[{\"category\":\"provider\",\"value\":\"ollama\",\"path\":\"src/local.py\",\"quote\":\"import ollama\"}],\"forbidden\":[]},{\"id\":\"code-019\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal ollama\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"Modelfile\",\"quote\":\"FROM llama3.1\"}],\"forbidden\":[]},{\"id\":\"code-020\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal mcp-filesystem\",\"facts\":[{\"category\":\"mcp\",\"value\":\"mcp-filesystem\",\"path\":\".vscode/mcp.json\",\"quote\":\"@modelcontextprotocol/server-filesystem\"}],\"forbidden\":[]},{\"id\":\"code-021\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal cursor\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\".cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-memory\"}],\"forbidden\":[]},{\"id\":\"code-022\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal openrouter\",\"facts\":[{\"category\":\"provider\",\"value\":\"openrouter\",\"path\":\"src/route.py\",\"quote\":\"https://openrouter.ai/api/v1\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"src/route.py\",\"quote\":\"from openai import OpenAI\"}],\"forbidden\":[]},{\"id\":\"code-023\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal aws-bedrock\",\"facts\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\",\"path\":\"src/bedrock_call.py\",\"quote\":\"boto3.client('bedrock-runtime')\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"src/bedrock_call.py\",\"quote\":\"anthropic.claude-3-haiku\"}],\"forbidden\":[]},{\"id\":\"code-024\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal semantic-kernel\",\"facts\":[{\"category\":\"framework\",\"value\":\"semantic-kernel\",\"path\":\"src/sk.py\",\"quote\":\"import semantic_kernel\"}],\"forbidden\":[]},{\"id\":\"code-025\",\"surface\":\"code\",\"polarity\":\"positive\",\"title\":\"Code signal a2a-card\",\"facts\":[{\"category\":\"a2a\",\"value\":\"a2a-card\",\"path\":\"agent-card.json\",\"quote\":\"\\\"protocol\\\": \\\"a2a\\\"\"}],\"forbidden\":[]},{\"id\":\"code-026\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary flask service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-027\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary requests service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-028\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary numpy service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-029\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary pandas service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-030\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary fastapi service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-031\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary click service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-032\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary pyyaml service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-033\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary rich service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-034\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary httpx service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-035\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary pydantic service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-036\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary sqlalchemy service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-037\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary pytest service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-038\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary typer service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-039\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary uvicorn service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-040\",\"surface\":\"code\",\"polarity\":\"negative\",\"title\":\"Ordinary jinja2 service\",\"facts\":[],\"forbidden\":[]},{\"id\":\"code-041\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Minecraft Bedrock notes\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"code-042\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"HTTP agent-base dependency\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"framework\",\"value\":\"autogen\"}]},{\"id\":\"code-043\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Prose mention of OpenAI\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"code-044\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"CSS cursor property\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"code-045\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Comment naming Claude Bernard\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"claude-code\"},{\"category\":\"provider\",\"value\":\"anthropic\"}]},{\"id\":\"code-046\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Travel agent prose\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"code-047\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Glossary initialism\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"code-048\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Minecraft hostname\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"code-049\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Express shop\",\"facts\":[],\"forbidden\":[{\"category\":\"framework\",\"value\":\"langchain\"}]},{\"id\":\"code-050\",\"surface\":\"code\",\"polarity\":\"near_miss\",\"title\":\"Human on-call copilot\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"github-copilot\"},{\"category\":\"saas_ai\",\"value\":\"microsoft-copilot\"}]},{\"id\":\"endpoint-001\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint cursor\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-002\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-code\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"},{\"category\":\"mcp\",\"value\":\"mcp-filesystem\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"}],\"forbidden\":[]},{\"id\":\"endpoint-003\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-desktop\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"},{\"category\":\"mcp\",\"value\":\"mcp-slack\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"}],\"forbidden\":[]},{\"id\":\"endpoint-004\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint gemini-cli\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"},{\"category\":\"mcp\",\"value\":\"mcp-memory\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"}],\"forbidden\":[]},{\"id\":\"endpoint-005\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-006\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint codex-cli\",\"facts\":[{\"category\":\"agent\",\"value\":\"codex-cli\",\"path\":\"home/.codex/config.toml\",\"quote\":\"mcp_servers.github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.codex/config.toml\",\"quote\":\"mcp_servers.github\"}],\"forbidden\":[]},{\"id\":\"endpoint-007\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint ollama\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"home/.ollama/models/manifests/registry.ollama.ai/library/llama3.1\",\"quote\":\"llama3.1\"}],\"forbidden\":[]},{\"id\":\"endpoint-008\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint continue\",\"facts\":[{\"category\":\"agent\",\"value\":\"continue\",\"path\":\"home/.continue/config.json\",\"quote\":\"\\\"provider\\\": \\\"openai\\\"\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"home/.continue/config.json\",\"quote\":\"\\\"provider\\\": \\\"openai\\\"\"}],\"forbidden\":[]},{\"id\":\"endpoint-009\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint github-copilot\",\"facts\":[{\"category\":\"agent\",\"value\":\"github-copilot\",\"path\":\"home/.config/Code/User/mcp.json\",\"quote\":\"server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.config/Code/User/mcp.json\",\"quote\":\"server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-010\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint openclaw\",\"facts\":[{\"category\":\"agent\",\"value\":\"openclaw\",\"path\":\"home/.openclaw/config.json\",\"quote\":\"\\\"agent\\\": \\\"openclaw\\\"\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"home/.openclaw/config.json\",\"quote\":\"\\\"agent\\\": \\\"openclaw\\\"\"}],\"forbidden\":[]},{\"id\":\"endpoint-011\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint cursor\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-012\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-code\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"},{\"category\":\"mcp\",\"value\":\"mcp-filesystem\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"}],\"forbidden\":[]},{\"id\":\"endpoint-013\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-desktop\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"},{\"category\":\"mcp\",\"value\":\"mcp-slack\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"}],\"forbidden\":[]},{\"id\":\"endpoint-014\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint gemini-cli\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"},{\"category\":\"mcp\",\"value\":\"mcp-memory\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"}],\"forbidden\":[]},{\"id\":\"endpoint-015\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-016\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint codex-cli\",\"facts\":[{\"category\":\"agent\",\"value\":\"codex-cli\",\"path\":\"home/.codex/config.toml\",\"quote\":\"mcp_servers.github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.codex/config.toml\",\"quote\":\"mcp_servers.github\"}],\"forbidden\":[]},{\"id\":\"endpoint-017\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint ollama\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"home/.ollama/models/manifests/registry.ollama.ai/library/llama3.1\",\"quote\":\"llama3.1\"}],\"forbidden\":[]},{\"id\":\"endpoint-018\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint continue\",\"facts\":[{\"category\":\"agent\",\"value\":\"continue\",\"path\":\"home/.continue/config.json\",\"quote\":\"\\\"provider\\\": \\\"openai\\\"\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"home/.continue/config.json\",\"quote\":\"\\\"provider\\\": \\\"openai\\\"\"}],\"forbidden\":[]},{\"id\":\"endpoint-019\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint github-copilot\",\"facts\":[{\"category\":\"agent\",\"value\":\"github-copilot\",\"path\":\"home/.config/Code/User/mcp.json\",\"quote\":\"server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.config/Code/User/mcp.json\",\"quote\":\"server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-020\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint openclaw\",\"facts\":[{\"category\":\"agent\",\"value\":\"openclaw\",\"path\":\"home/.openclaw/config.json\",\"quote\":\"\\\"agent\\\": \\\"openclaw\\\"\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"home/.openclaw/config.json\",\"quote\":\"\\\"agent\\\": \\\"openclaw\\\"\"}],\"forbidden\":[]},{\"id\":\"endpoint-021\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint cursor\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.cursor/mcp.json\",\"quote\":\"@modelcontextprotocol/server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-022\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-code\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"},{\"category\":\"mcp\",\"value\":\"mcp-filesystem\",\"path\":\"home/.claude.json\",\"quote\":\"server-filesystem\"}],\"forbidden\":[]},{\"id\":\"endpoint-023\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint claude-desktop\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"},{\"category\":\"mcp\",\"value\":\"mcp-slack\",\"path\":\"home/.config/Claude/claude_desktop_config.json\",\"quote\":\"server-slack\"}],\"forbidden\":[]},{\"id\":\"endpoint-024\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint gemini-cli\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"},{\"category\":\"mcp\",\"value\":\"mcp-memory\",\"path\":\"home/.gemini/settings.json\",\"quote\":\"server-memory\"}],\"forbidden\":[]},{\"id\":\"endpoint-025\",\"surface\":\"endpoint\",\"polarity\":\"positive\",\"title\":\"Endpoint windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"},{\"category\":\"mcp\",\"value\":\"mcp-github\",\"path\":\"home/.codeium/windsurf/mcp_config.json\",\"quote\":\"server-github\"}],\"forbidden\":[]},{\"id\":\"endpoint-026\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-027\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-028\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-029\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-030\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-031\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-032\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-033\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-034\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-035\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-036\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-037\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-038\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-039\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-040\",\"surface\":\"endpoint\",\"polarity\":\"negative\",\"title\":\"Quiet home directory\",\"facts\":[],\"forbidden\":[]},{\"id\":\"endpoint-041\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-042\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-043\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-044\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-045\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-046\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-047\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-048\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-049\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"endpoint-050\",\"surface\":\"endpoint\",\"polarity\":\"near_miss\",\"title\":\"Home directory with prose and CSS\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"},{\"category\":\"agent\",\"value\":\"claude-code\"}]},{\"id\":\"gateway-001\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"spend.jsonl\",\"quote\":\"gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-002\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call claude-3-5-sonnet\",\"facts\":[{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"spend.jsonl\",\"quote\":\"claude-3-5-sonnet\"}],\"forbidden\":[]},{\"id\":\"gateway-003\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gemini-1.5-pro\",\"facts\":[{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"spend.jsonl\",\"quote\":\"gemini-1.5-pro\"}],\"forbidden\":[]},{\"id\":\"gateway-004\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call mistral-large\",\"facts\":[{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"spend.jsonl\",\"quote\":\"mistral-large\"}],\"forbidden\":[]},{\"id\":\"gateway-005\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call llama-3.1-70b\",\"facts\":[{\"category\":\"provider\",\"value\":\"groq\",\"path\":\"spend.jsonl\",\"quote\":\"llama-3.1-70b\"}],\"forbidden\":[]},{\"id\":\"gateway-006\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call command-r-plus\",\"facts\":[{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"spend.jsonl\",\"quote\":\"command-r-plus\"}],\"forbidden\":[]},{\"id\":\"gateway-007\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call openai/gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openrouter\",\"path\":\"spend.jsonl\",\"quote\":\"openai/gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-008\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"spend.jsonl\",\"quote\":\"gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-009\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call claude-3-5-sonnet\",\"facts\":[{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"spend.jsonl\",\"quote\":\"claude-3-5-sonnet\"}],\"forbidden\":[]},{\"id\":\"gateway-010\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gemini-1.5-pro\",\"facts\":[{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"spend.jsonl\",\"quote\":\"gemini-1.5-pro\"}],\"forbidden\":[]},{\"id\":\"gateway-011\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call mistral-large\",\"facts\":[{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"spend.jsonl\",\"quote\":\"mistral-large\"}],\"forbidden\":[]},{\"id\":\"gateway-012\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call llama-3.1-70b\",\"facts\":[{\"category\":\"provider\",\"value\":\"groq\",\"path\":\"spend.jsonl\",\"quote\":\"llama-3.1-70b\"}],\"forbidden\":[]},{\"id\":\"gateway-013\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call command-r-plus\",\"facts\":[{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"spend.jsonl\",\"quote\":\"command-r-plus\"}],\"forbidden\":[]},{\"id\":\"gateway-014\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call openai/gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openrouter\",\"path\":\"spend.jsonl\",\"quote\":\"openai/gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-015\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"spend.jsonl\",\"quote\":\"gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-016\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call claude-3-5-sonnet\",\"facts\":[{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"spend.jsonl\",\"quote\":\"claude-3-5-sonnet\"}],\"forbidden\":[]},{\"id\":\"gateway-017\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gemini-1.5-pro\",\"facts\":[{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"spend.jsonl\",\"quote\":\"gemini-1.5-pro\"}],\"forbidden\":[]},{\"id\":\"gateway-018\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call mistral-large\",\"facts\":[{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"spend.jsonl\",\"quote\":\"mistral-large\"}],\"forbidden\":[]},{\"id\":\"gateway-019\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call llama-3.1-70b\",\"facts\":[{\"category\":\"provider\",\"value\":\"groq\",\"path\":\"spend.jsonl\",\"quote\":\"llama-3.1-70b\"}],\"forbidden\":[]},{\"id\":\"gateway-020\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call command-r-plus\",\"facts\":[{\"category\":\"provider\",\"value\":\"cohere\",\"path\":\"spend.jsonl\",\"quote\":\"command-r-plus\"}],\"forbidden\":[]},{\"id\":\"gateway-021\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call openai/gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openrouter\",\"path\":\"spend.jsonl\",\"quote\":\"openai/gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-022\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gpt-4o\",\"facts\":[{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"spend.jsonl\",\"quote\":\"gpt-4o\"}],\"forbidden\":[]},{\"id\":\"gateway-023\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call claude-3-5-sonnet\",\"facts\":[{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"spend.jsonl\",\"quote\":\"claude-3-5-sonnet\"}],\"forbidden\":[]},{\"id\":\"gateway-024\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call gemini-1.5-pro\",\"facts\":[{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"spend.jsonl\",\"quote\":\"gemini-1.5-pro\"}],\"forbidden\":[]},{\"id\":\"gateway-025\",\"surface\":\"gateway\",\"polarity\":\"positive\",\"title\":\"Gateway call mistral-large\",\"facts\":[{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"spend.jsonl\",\"quote\":\"mistral-large\"}],\"forbidden\":[]},{\"id\":\"gateway-026\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-027\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-028\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-029\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-030\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-031\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-032\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-033\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-034\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-035\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-036\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-037\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-038\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-039\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-040\",\"surface\":\"gateway\",\"polarity\":\"negative\",\"title\":\"Gateway call to GitHub REST\",\"facts\":[],\"forbidden\":[]},{\"id\":\"gateway-041\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-042\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-043\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-044\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-045\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-046\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-047\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-048\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-049\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"gateway-050\",\"surface\":\"gateway\",\"polarity\":\"near_miss\",\"title\":\"Gateway row for a game status host\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"aws-bedrock\"},{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"identity-001\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant ChatGPT\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"chatgpt\",\"path\":\"okta-apps.json\",\"quote\":\"ChatGPT\"}],\"forbidden\":[]},{\"id\":\"identity-002\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Claude\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"claude\",\"path\":\"okta-apps.json\",\"quote\":\"Claude\"}],\"forbidden\":[]},{\"id\":\"identity-003\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Gemini\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"gemini\",\"path\":\"okta-apps.json\",\"quote\":\"Gemini\"}],\"forbidden\":[]},{\"id\":\"identity-004\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant GitHub Copilot\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"github-copilot\",\"path\":\"okta-apps.json\",\"quote\":\"GitHub Copilot\"}],\"forbidden\":[]},{\"id\":\"identity-005\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Notion AI\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"notion-ai\",\"path\":\"okta-apps.json\",\"quote\":\"Notion AI\"}],\"forbidden\":[]},{\"id\":\"identity-006\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Microsoft Copilot\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"microsoft-copilot\",\"path\":\"okta-apps.json\",\"quote\":\"Microsoft Copilot\"}],\"forbidden\":[]},{\"id\":\"identity-007\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Perplexity\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"perplexity\",\"path\":\"okta-apps.json\",\"quote\":\"Perplexity\"}],\"forbidden\":[]},{\"id\":\"identity-008\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Cursor\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"cursor\",\"path\":\"okta-apps.json\",\"quote\":\"Cursor\"}],\"forbidden\":[]},{\"id\":\"identity-009\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Mistral\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"mistral\",\"path\":\"okta-apps.json\",\"quote\":\"Mistral\"}],\"forbidden\":[]},{\"id\":\"identity-010\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Groq\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"groq\",\"path\":\"okta-apps.json\",\"quote\":\"Groq\"}],\"forbidden\":[]},{\"id\":\"identity-011\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Cohere\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"cohere\",\"path\":\"okta-apps.json\",\"quote\":\"Cohere\"}],\"forbidden\":[]},{\"id\":\"identity-012\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Midjourney\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"midjourney\",\"path\":\"okta-apps.json\",\"quote\":\"Midjourney\"}],\"forbidden\":[]},{\"id\":\"identity-013\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant ElevenLabs\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"elevenlabs\",\"path\":\"okta-apps.json\",\"quote\":\"ElevenLabs\"}],\"forbidden\":[]},{\"id\":\"identity-014\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Runway\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"runway\",\"path\":\"okta-apps.json\",\"quote\":\"Runway\"}],\"forbidden\":[]},{\"id\":\"identity-015\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Character.AI\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"character-ai\",\"path\":\"okta-apps.json\",\"quote\":\"Character.AI\"}],\"forbidden\":[]},{\"id\":\"identity-016\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Poe\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"poe\",\"path\":\"okta-apps.json\",\"quote\":\"Poe\"}],\"forbidden\":[]},{\"id\":\"identity-017\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Phind\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"phind\",\"path\":\"okta-apps.json\",\"quote\":\"Phind\"}],\"forbidden\":[]},{\"id\":\"identity-018\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Codeium\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"codeium\",\"path\":\"okta-apps.json\",\"quote\":\"Codeium\"}],\"forbidden\":[]},{\"id\":\"identity-019\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Tabnine\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"tabnine\",\"path\":\"okta-apps.json\",\"quote\":\"Tabnine\"}],\"forbidden\":[]},{\"id\":\"identity-020\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Sourcegraph Cody\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"cody\",\"path\":\"okta-apps.json\",\"quote\":\"Sourcegraph Cody\"}],\"forbidden\":[]},{\"id\":\"identity-021\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Amazon Q\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"amazon-q\",\"path\":\"okta-apps.json\",\"quote\":\"Amazon Q\"}],\"forbidden\":[]},{\"id\":\"identity-022\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Jasper\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"jasper\",\"path\":\"okta-apps.json\",\"quote\":\"Jasper\"}],\"forbidden\":[]},{\"id\":\"identity-023\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Copy.ai\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"copy-ai\",\"path\":\"okta-apps.json\",\"quote\":\"Copy.ai\"}],\"forbidden\":[]},{\"id\":\"identity-024\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant You.com\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"you-com\",\"path\":\"okta-apps.json\",\"quote\":\"You.com\"}],\"forbidden\":[]},{\"id\":\"identity-025\",\"surface\":\"identity\",\"polarity\":\"positive\",\"title\":\"Okta grant Hugging Face\",\"facts\":[{\"category\":\"identity_grant\",\"value\":\"huggingface\",\"path\":\"okta-apps.json\",\"quote\":\"Hugging Face\"}],\"forbidden\":[]},{\"id\":\"identity-026\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Workday\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-027\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant DocuSign\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-028\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Zendesk\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-029\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant PagerDuty\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-030\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Figma\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-031\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Box\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-032\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Dropbox\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-033\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Datadog\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-034\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant ServiceNow ITSM\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-035\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Jira\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-036\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Okta Dashboard\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-037\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Salesforce CRM\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-038\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Zoom Meetings\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-039\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant Slack\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-040\",\"surface\":\"identity\",\"polarity\":\"negative\",\"title\":\"Okta grant GitHub\",\"facts\":[],\"forbidden\":[]},{\"id\":\"identity-041\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Claude Bernard Gallery\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"claude\"}]},{\"id\":\"identity-042\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Cursor Manufacturing ERP\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"cursor\"}]},{\"id\":\"identity-043\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Gemini Freight Lines\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"gemini\"}]},{\"id\":\"identity-044\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Copilot Insurance Agency\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"github-copilot\"}]},{\"id\":\"identity-045\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Bedrock Landscaping\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"identity-046\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Agent Provocateur HR\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"chatgpt\"}]},{\"id\":\"identity-047\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Einstein Bros Catering\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"salesforce-einstein\"}]},{\"id\":\"identity-048\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Open Air Travel\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"identity-049\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss Notion Template Club\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"notion-ai\"}]},{\"id\":\"identity-050\",\"surface\":\"identity\",\"polarity\":\"near_miss\",\"title\":\"Okta near-miss AI Book Club\",\"facts\":[],\"forbidden\":[{\"category\":\"identity_grant\",\"value\":\"slack-ai\"}]},{\"id\":\"lowcode-001\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.openAi\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-002\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.anthropic\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-003\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.googleGemini\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-004\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.mistral\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-005\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.agent\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-agent\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"}],\"forbidden\":[]},{\"id\":\"lowcode-006\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.openAi\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-007\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.anthropic\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-008\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.googleGemini\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-009\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.mistral\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-010\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.agent\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-agent\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"}],\"forbidden\":[]},{\"id\":\"lowcode-011\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.openAi\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-012\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.anthropic\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-013\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.googleGemini\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-014\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.mistral\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-015\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.agent\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-agent\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"}],\"forbidden\":[]},{\"id\":\"lowcode-016\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.openAi\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-017\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.anthropic\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-018\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.googleGemini\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-019\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.mistral\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-020\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.agent\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-agent\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"}],\"forbidden\":[]},{\"id\":\"lowcode-021\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.openAi\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"provider\",\"value\":\"openai\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.openAi\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-022\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.anthropic\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"provider\",\"value\":\"anthropic\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.anthropic\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-023\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.googleGemini\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"provider\",\"value\":\"google-gemini\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.googleGemini\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-024\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.mistral\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"provider\",\"value\":\"mistral\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.mistral\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"langchain\"}],\"forbidden\":[]},{\"id\":\"lowcode-025\",\"surface\":\"lowcode\",\"polarity\":\"positive\",\"title\":\"n8n node @n8n/n8n-nodes-langchain.agent\",\"facts\":[{\"category\":\"lowcode\",\"value\":\"n8n-agent\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"},{\"category\":\"framework\",\"value\":\"langchain\",\"path\":\"workflow.json\",\"quote\":\"@n8n/n8n-nodes-langchain.agent\"}],\"forbidden\":[]},{\"id\":\"lowcode-026\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-027\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-028\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-029\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-030\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-031\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-032\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-033\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-034\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-035\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-036\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-037\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-038\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-039\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-040\",\"surface\":\"lowcode\",\"polarity\":\"negative\",\"title\":\"n8n spreadsheet workflow\",\"facts\":[],\"forbidden\":[]},{\"id\":\"lowcode-041\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-042\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-043\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-044\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-045\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-046\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-047\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-048\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-049\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"lowcode-050\",\"surface\":\"lowcode\",\"polarity\":\"near_miss\",\"title\":\"n8n webhook named AI ideas\",\"facts\":[],\"forbidden\":[{\"category\":\"lowcode\",\"value\":\"n8n-openai\"},{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"network-001\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.openai.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"openai\",\"path\":\"dns.jsonl\",\"quote\":\"api.openai.com\"}],\"forbidden\":[]},{\"id\":\"network-002\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.anthropic.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"anthropic\",\"path\":\"dns.jsonl\",\"quote\":\"api.anthropic.com\"}],\"forbidden\":[]},{\"id\":\"network-003\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query generativelanguage.googleapis.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"google-gemini\",\"path\":\"dns.jsonl\",\"quote\":\"generativelanguage.googleapis.com\"}],\"forbidden\":[]},{\"id\":\"network-004\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.mistral.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"mistral\",\"path\":\"dns.jsonl\",\"quote\":\"api.mistral.ai\"}],\"forbidden\":[]},{\"id\":\"network-005\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.groq.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"groq\",\"path\":\"dns.jsonl\",\"quote\":\"api.groq.com\"}],\"forbidden\":[]},{\"id\":\"network-006\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.cohere.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"cohere\",\"path\":\"dns.jsonl\",\"quote\":\"api.cohere.ai\"}],\"forbidden\":[]},{\"id\":\"network-007\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query openrouter.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"openrouter\",\"path\":\"dns.jsonl\",\"quote\":\"openrouter.ai\"}],\"forbidden\":[]},{\"id\":\"network-008\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.openai.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"openai\",\"path\":\"dns.jsonl\",\"quote\":\"api.openai.com\"}],\"forbidden\":[]},{\"id\":\"network-009\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.anthropic.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"anthropic\",\"path\":\"dns.jsonl\",\"quote\":\"api.anthropic.com\"}],\"forbidden\":[]},{\"id\":\"network-010\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query generativelanguage.googleapis.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"google-gemini\",\"path\":\"dns.jsonl\",\"quote\":\"generativelanguage.googleapis.com\"}],\"forbidden\":[]},{\"id\":\"network-011\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.mistral.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"mistral\",\"path\":\"dns.jsonl\",\"quote\":\"api.mistral.ai\"}],\"forbidden\":[]},{\"id\":\"network-012\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.groq.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"groq\",\"path\":\"dns.jsonl\",\"quote\":\"api.groq.com\"}],\"forbidden\":[]},{\"id\":\"network-013\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.cohere.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"cohere\",\"path\":\"dns.jsonl\",\"quote\":\"api.cohere.ai\"}],\"forbidden\":[]},{\"id\":\"network-014\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query openrouter.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"openrouter\",\"path\":\"dns.jsonl\",\"quote\":\"openrouter.ai\"}],\"forbidden\":[]},{\"id\":\"network-015\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.openai.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"openai\",\"path\":\"dns.jsonl\",\"quote\":\"api.openai.com\"}],\"forbidden\":[]},{\"id\":\"network-016\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.anthropic.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"anthropic\",\"path\":\"dns.jsonl\",\"quote\":\"api.anthropic.com\"}],\"forbidden\":[]},{\"id\":\"network-017\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query generativelanguage.googleapis.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"google-gemini\",\"path\":\"dns.jsonl\",\"quote\":\"generativelanguage.googleapis.com\"}],\"forbidden\":[]},{\"id\":\"network-018\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.mistral.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"mistral\",\"path\":\"dns.jsonl\",\"quote\":\"api.mistral.ai\"}],\"forbidden\":[]},{\"id\":\"network-019\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.groq.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"groq\",\"path\":\"dns.jsonl\",\"quote\":\"api.groq.com\"}],\"forbidden\":[]},{\"id\":\"network-020\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.cohere.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"cohere\",\"path\":\"dns.jsonl\",\"quote\":\"api.cohere.ai\"}],\"forbidden\":[]},{\"id\":\"network-021\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query openrouter.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"openrouter\",\"path\":\"dns.jsonl\",\"quote\":\"openrouter.ai\"}],\"forbidden\":[]},{\"id\":\"network-022\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.openai.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"openai\",\"path\":\"dns.jsonl\",\"quote\":\"api.openai.com\"}],\"forbidden\":[]},{\"id\":\"network-023\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.anthropic.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"anthropic\",\"path\":\"dns.jsonl\",\"quote\":\"api.anthropic.com\"}],\"forbidden\":[]},{\"id\":\"network-024\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query generativelanguage.googleapis.com\",\"facts\":[{\"category\":\"egress\",\"value\":\"google-gemini\",\"path\":\"dns.jsonl\",\"quote\":\"generativelanguage.googleapis.com\"}],\"forbidden\":[]},{\"id\":\"network-025\",\"surface\":\"network\",\"polarity\":\"positive\",\"title\":\"DNS query api.mistral.ai\",\"facts\":[{\"category\":\"egress\",\"value\":\"mistral\",\"path\":\"dns.jsonl\",\"quote\":\"api.mistral.ai\"}],\"forbidden\":[]},{\"id\":\"network-026\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-027\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-028\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-029\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-030\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-031\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-032\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-033\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-034\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-035\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-036\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-037\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-038\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-039\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-040\",\"surface\":\"network\",\"polarity\":\"negative\",\"title\":\"DNS query for Microsoft login\",\"facts\":[],\"forbidden\":[]},{\"id\":\"network-041\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-042\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-043\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-044\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-045\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-046\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-047\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-048\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-049\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"network-050\",\"surface\":\"network\",\"polarity\":\"near_miss\",\"title\":\"DNS query for a game host\",\"facts\":[],\"forbidden\":[{\"category\":\"egress\",\"value\":\"aws-bedrock\"},{\"category\":\"provider\",\"value\":\"aws-bedrock\"}]},{\"id\":\"runtime-001\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"processes.json\",\"quote\":\"claude\"}],\"forbidden\":[]},{\"id\":\"runtime-002\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process /opt/Claude/claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"processes.json\",\"quote\":\"/opt/Claude/claude\"}],\"forbidden\":[]},{\"id\":\"runtime-003\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process cursor .\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"processes.json\",\"quote\":\"cursor .\"}],\"forbidden\":[]},{\"id\":\"runtime-004\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process ollama serve\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"processes.json\",\"quote\":\"ollama serve\"}],\"forbidden\":[]},{\"id\":\"runtime-005\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process gemini\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"processes.json\",\"quote\":\"gemini\"}],\"forbidden\":[]},{\"id\":\"runtime-006\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process codex\",\"facts\":[{\"category\":\"agent\",\"value\":\"codex-cli\",\"path\":\"processes.json\",\"quote\":\"codex\"}],\"forbidden\":[]},{\"id\":\"runtime-007\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"processes.json\",\"quote\":\"windsurf\"}],\"forbidden\":[]},{\"id\":\"runtime-008\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process openclaw\",\"facts\":[{\"category\":\"agent\",\"value\":\"openclaw\",\"path\":\"processes.json\",\"quote\":\"openclaw\"}],\"forbidden\":[]},{\"id\":\"runtime-009\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"processes.json\",\"quote\":\"claude\"}],\"forbidden\":[]},{\"id\":\"runtime-010\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process /opt/Claude/claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"processes.json\",\"quote\":\"/opt/Claude/claude\"}],\"forbidden\":[]},{\"id\":\"runtime-011\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process cursor .\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"processes.json\",\"quote\":\"cursor .\"}],\"forbidden\":[]},{\"id\":\"runtime-012\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process ollama serve\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"processes.json\",\"quote\":\"ollama serve\"}],\"forbidden\":[]},{\"id\":\"runtime-013\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process gemini\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"processes.json\",\"quote\":\"gemini\"}],\"forbidden\":[]},{\"id\":\"runtime-014\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process codex\",\"facts\":[{\"category\":\"agent\",\"value\":\"codex-cli\",\"path\":\"processes.json\",\"quote\":\"codex\"}],\"forbidden\":[]},{\"id\":\"runtime-015\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"processes.json\",\"quote\":\"windsurf\"}],\"forbidden\":[]},{\"id\":\"runtime-016\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process openclaw\",\"facts\":[{\"category\":\"agent\",\"value\":\"openclaw\",\"path\":\"processes.json\",\"quote\":\"openclaw\"}],\"forbidden\":[]},{\"id\":\"runtime-017\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"processes.json\",\"quote\":\"claude\"}],\"forbidden\":[]},{\"id\":\"runtime-018\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process /opt/Claude/claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-desktop\",\"path\":\"processes.json\",\"quote\":\"/opt/Claude/claude\"}],\"forbidden\":[]},{\"id\":\"runtime-019\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process cursor .\",\"facts\":[{\"category\":\"agent\",\"value\":\"cursor\",\"path\":\"processes.json\",\"quote\":\"cursor .\"}],\"forbidden\":[]},{\"id\":\"runtime-020\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process ollama serve\",\"facts\":[{\"category\":\"local_model\",\"value\":\"ollama\",\"path\":\"processes.json\",\"quote\":\"ollama serve\"}],\"forbidden\":[]},{\"id\":\"runtime-021\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process gemini\",\"facts\":[{\"category\":\"agent\",\"value\":\"gemini-cli\",\"path\":\"processes.json\",\"quote\":\"gemini\"}],\"forbidden\":[]},{\"id\":\"runtime-022\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process codex\",\"facts\":[{\"category\":\"agent\",\"value\":\"codex-cli\",\"path\":\"processes.json\",\"quote\":\"codex\"}],\"forbidden\":[]},{\"id\":\"runtime-023\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process windsurf\",\"facts\":[{\"category\":\"agent\",\"value\":\"windsurf\",\"path\":\"processes.json\",\"quote\":\"windsurf\"}],\"forbidden\":[]},{\"id\":\"runtime-024\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process openclaw\",\"facts\":[{\"category\":\"agent\",\"value\":\"openclaw\",\"path\":\"processes.json\",\"quote\":\"openclaw\"}],\"forbidden\":[]},{\"id\":\"runtime-025\",\"surface\":\"runtime\",\"polarity\":\"positive\",\"title\":\"Process claude\",\"facts\":[{\"category\":\"agent\",\"value\":\"claude-code\",\"path\":\"processes.json\",\"quote\":\"claude\"}],\"forbidden\":[]},{\"id\":\"runtime-026\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-027\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-028\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-029\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-030\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-031\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-032\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-033\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-034\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-035\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-036\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-037\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-038\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-039\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-040\",\"surface\":\"runtime\",\"polarity\":\"negative\",\"title\":\"nginx worker\",\"facts\":[],\"forbidden\":[]},{\"id\":\"runtime-041\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-042\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-043\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-044\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-045\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-046\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-047\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-048\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-049\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"runtime-050\",\"surface\":\"runtime\",\"polarity\":\"near_miss\",\"title\":\"Unrelated cursor-blink process\",\"facts\":[],\"forbidden\":[{\"category\":\"agent\",\"value\":\"cursor\"}]},{\"id\":\"saas-001\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app ChatGPT\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"chatgpt\",\"path\":\"approved-app.json\",\"quote\":\"ChatGPT\"}],\"forbidden\":[]},{\"id\":\"saas-002\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Claude\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"claude\",\"path\":\"approved-app.json\",\"quote\":\"Claude\"}],\"forbidden\":[]},{\"id\":\"saas-003\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Gemini\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"gemini\",\"path\":\"approved-app.json\",\"quote\":\"Gemini\"}],\"forbidden\":[]},{\"id\":\"saas-004\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app GitHub Copilot\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"github-copilot\",\"path\":\"approved-app.json\",\"quote\":\"GitHub Copilot\"}],\"forbidden\":[]},{\"id\":\"saas-005\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Notion AI\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"notion-ai\",\"path\":\"approved-app.json\",\"quote\":\"Notion AI\"}],\"forbidden\":[]},{\"id\":\"saas-006\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Microsoft Copilot\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"microsoft-copilot\",\"path\":\"approved-app.json\",\"quote\":\"Microsoft Copilot\"}],\"forbidden\":[]},{\"id\":\"saas-007\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Perplexity\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"perplexity\",\"path\":\"approved-app.json\",\"quote\":\"Perplexity\"}],\"forbidden\":[]},{\"id\":\"saas-008\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Cursor\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"cursor\",\"path\":\"approved-app.json\",\"quote\":\"Cursor\"}],\"forbidden\":[]},{\"id\":\"saas-009\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Mistral\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"mistral\",\"path\":\"approved-app.json\",\"quote\":\"Mistral\"}],\"forbidden\":[]},{\"id\":\"saas-010\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Groq\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"groq\",\"path\":\"approved-app.json\",\"quote\":\"Groq\"}],\"forbidden\":[]},{\"id\":\"saas-011\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Cohere\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"cohere\",\"path\":\"approved-app.json\",\"quote\":\"Cohere\"}],\"forbidden\":[]},{\"id\":\"saas-012\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Midjourney\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"midjourney\",\"path\":\"approved-app.json\",\"quote\":\"Midjourney\"}],\"forbidden\":[]},{\"id\":\"saas-013\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app ElevenLabs\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"elevenlabs\",\"path\":\"approved-app.json\",\"quote\":\"ElevenLabs\"}],\"forbidden\":[]},{\"id\":\"saas-014\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Runway\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"runway\",\"path\":\"approved-app.json\",\"quote\":\"Runway\"}],\"forbidden\":[]},{\"id\":\"saas-015\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Character.AI\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"character-ai\",\"path\":\"approved-app.json\",\"quote\":\"Character.AI\"}],\"forbidden\":[]},{\"id\":\"saas-016\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Poe\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"poe\",\"path\":\"approved-app.json\",\"quote\":\"Poe\"}],\"forbidden\":[]},{\"id\":\"saas-017\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Phind\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"phind\",\"path\":\"approved-app.json\",\"quote\":\"Phind\"}],\"forbidden\":[]},{\"id\":\"saas-018\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Codeium\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"codeium\",\"path\":\"approved-app.json\",\"quote\":\"Codeium\"}],\"forbidden\":[]},{\"id\":\"saas-019\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Tabnine\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"tabnine\",\"path\":\"approved-app.json\",\"quote\":\"Tabnine\"}],\"forbidden\":[]},{\"id\":\"saas-020\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Sourcegraph Cody\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"cody\",\"path\":\"approved-app.json\",\"quote\":\"Sourcegraph Cody\"}],\"forbidden\":[]},{\"id\":\"saas-021\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Amazon Q\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"amazon-q\",\"path\":\"approved-app.json\",\"quote\":\"Amazon Q\"}],\"forbidden\":[]},{\"id\":\"saas-022\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Jasper\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"jasper\",\"path\":\"approved-app.json\",\"quote\":\"Jasper\"}],\"forbidden\":[]},{\"id\":\"saas-023\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Copy.ai\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"copy-ai\",\"path\":\"approved-app.json\",\"quote\":\"Copy.ai\"}],\"forbidden\":[]},{\"id\":\"saas-024\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app You.com\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"you-com\",\"path\":\"approved-app.json\",\"quote\":\"You.com\"}],\"forbidden\":[]},{\"id\":\"saas-025\",\"surface\":\"saas\",\"polarity\":\"positive\",\"title\":\"Slack app Hugging Face\",\"facts\":[{\"category\":\"saas_ai\",\"value\":\"huggingface\",\"path\":\"approved-app.json\",\"quote\":\"Hugging Face\"}],\"forbidden\":[]},{\"id\":\"saas-026\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Workday\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-027\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app DocuSign\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-028\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Zendesk\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-029\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app PagerDuty\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-030\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Figma\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-031\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Box\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-032\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Dropbox\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-033\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Datadog\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-034\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app ServiceNow ITSM\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-035\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Jira\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-036\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Okta Dashboard\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-037\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Salesforce CRM\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-038\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Zoom Meetings\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-039\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app Slack\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-040\",\"surface\":\"saas\",\"polarity\":\"negative\",\"title\":\"Slack app GitHub\",\"facts\":[],\"forbidden\":[]},{\"id\":\"saas-041\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Claude Bernard Gallery\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"claude\"}]},{\"id\":\"saas-042\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Cursor Manufacturing ERP\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"cursor\"}]},{\"id\":\"saas-043\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Gemini Freight Lines\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"gemini\"}]},{\"id\":\"saas-044\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Copilot Insurance Agency\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"github-copilot\"}]},{\"id\":\"saas-045\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Bedrock Landscaping\",\"facts\":[],\"forbidden\":[{\"category\":\"cloud_agent\",\"value\":\"bedrock-agent\"}]},{\"id\":\"saas-046\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Agent Provocateur HR\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"chatgpt\"}]},{\"id\":\"saas-047\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Einstein Bros Catering\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"salesforce-einstein\"}]},{\"id\":\"saas-048\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Open Air Travel\",\"facts\":[],\"forbidden\":[{\"category\":\"provider\",\"value\":\"openai\"}]},{\"id\":\"saas-049\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss Notion Template Club\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"notion-ai\"}]},{\"id\":\"saas-050\",\"surface\":\"saas\",\"polarity\":\"near_miss\",\"title\":\"Slack near-miss AI Book Club\",\"facts\":[],\"forbidden\":[{\"category\":\"saas_ai\",\"value\":\"slack-ai\"}]}]");
var SURFACES = [
	"code",
	"identity",
	"gateway",
	"lowcode",
	"saas",
	"cloud",
	"endpoint",
	"network",
	"runtime"
];
var NAMES = {
	shadowscan: "ShadowScan",
	vet: "SafeDep vet",
	numbat: "Perplexity Numbat",
	"snyk-agent-scan": "Snyk Agent Scan",
	"ai-bom": "Trusera ai-bom",
	nuguard: "NuGuard",
	agentdiscover: "AgentDiscover",
	"agentic-radar": "Agentic Radar",
	aiostack: "Aurva AIOstack",
	curatedmcp: "CuratedMCP",
	"reference-lexicon": "Lexicon reference"
};
var board = scoreboard_default;
var library = cases_default;
function pct(value) {
	if (value === null || value === void 0 || Number.isNaN(value)) return "—";
	return `${Math.round(value * 1e3) / 10}%`;
}
function num(value) {
	if (value === null || value === void 0 || Number.isNaN(value)) return "—";
	return value.toFixed(2);
}
function Home() {
	const tools = board.tools;
	const products = tools.filter((tool) => tool.role === "tool");
	const [tab, setTab] = (0, import_react.useState)("board");
	const [selected, setSelected] = (0, import_react.useState)(products.find((tool) => tool.status === "scored")?.id ?? products[0]?.id ?? "");
	const [surface, setSurface] = (0, import_react.useState)("all");
	const [polarity, setPolarity] = (0, import_react.useState)("all");
	const [query, setQuery] = (0, import_react.useState)("");
	const active = tools.find((tool) => tool.id === selected);
	const chart = products.filter((tool) => tool.metrics).map((tool) => ({
		name: NAMES[tool.id] ?? tool.id,
		f1: Math.round((tool.metrics?.quality.fact.f1 ?? 0) * 1e3) / 10
	}));
	const visibleCases = (0, import_react.useMemo)(() => {
		const needle = query.trim().toLowerCase();
		return library.filter((item) => {
			if (surface !== "all" && item.surface !== surface) return false;
			if (polarity !== "all" && item.polarity !== polarity) return false;
			if (!needle) return true;
			return `${item.id} ${item.title} ${item.facts.map((fact) => fact.value).join(" ")}`.toLowerCase().includes(needle);
		});
	}, [
		polarity,
		query,
		surface
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "mx-auto max-w-6xl px-4 py-8 sm:px-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "flex flex-col gap-6 border-b border-line pb-8 sm:flex-row sm:items-end sm:justify-between",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "max-w-2xl",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mb-3 flex items-center gap-2 text-accent",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScanSearch, {
								className: "size-5",
								"aria-hidden": "true"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "font-mono text-xs tracking-widest uppercase",
								children: "Discovery benchmark"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
							className: "text-3xl font-semibold tracking-tight sm:text-4xl",
							children: board.benchmark.name
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 text-base leading-relaxed text-muted",
							children: "Nine surfaces, fifty cases each. Labels are planted evidence, not the output of any scanner. In-scope F1 only counts surfaces a tool can actually read."
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-4 flex flex-wrap gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
								className: "cursor-pointer rounded-full border border-line bg-surface px-4 py-2 text-sm text-ink",
								href: "/shadowbench-report.html",
								target: "_blank",
								rel: "noreferrer",
								children: "HTML report"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
								className: "cursor-pointer rounded-full bg-ink px-4 py-2 text-sm text-paper",
								href: "/shadowbench-report.pdf",
								download: "ShadowBench.pdf",
								children: "PDF report"
							})]
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
					className: "grid grid-cols-2 gap-x-6 gap-y-2 font-mono text-xs text-muted",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", { children: "Cases" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
							className: "text-sm text-ink",
							children: board.benchmark.cases
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", { children: "Seed" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
							className: "text-sm text-ink",
							children: board.benchmark.seed
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "col-span-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", { children: "Corpus" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
								className: "truncate text-sm text-ink",
								children: board.benchmark.corpus_sha256
							})]
						})
					]
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
				className: "mt-6 flex gap-2",
				"aria-label": "Sections",
				children: [
					["board", "Scoreboard"],
					["cases", "Cases"],
					["method", "Method"]
				].map(([id, label]) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					onClick: () => setTab(id),
					className: tab === id ? "rounded-full bg-ink px-4 py-2 text-sm text-paper" : "rounded-full border border-line bg-surface px-4 py-2 text-sm text-ink",
					children: label
				}, id))
			}),
			tab === "board" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-8 flex flex-col gap-8",
				children: [
					products.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "rounded-lg border border-line bg-surface p-4 text-sm text-muted",
						children: "The scoring run has not been copied into this view yet."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "overflow-x-auto rounded-lg border border-line bg-surface",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
							className: "w-full min-w-[44rem] text-left text-sm",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", {
								className: "border-b border-line text-xs tracking-wide text-muted uppercase",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", { children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Tool"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Status"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Precision"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Recall"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "F1"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Specificity"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
										className: "px-4 py-3 font-medium",
										children: "Estate recall"
									})
								] })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tbody", { children: [products.map((tool) => {
								const fact = tool.metrics?.quality.fact;
								const on = tool.id === selected;
								return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
									className: on ? "bg-accent-soft" : "border-t border-line",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
												type: "button",
												className: "text-left",
												onClick: () => setSelected(tool.id),
												children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "font-medium",
													children: NAMES[tool.id] ?? tool.id
												})
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 text-muted",
											children: tool.status === "scored" ? "Scored" : "Not run"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.precision)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.recall)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.f1)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(tool.metrics?.quality.case.specificity)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(tool.metrics?.estate_recall)
										})
									]
								}, tool.id);
							}), tools.filter((tool) => tool.role === "reference").map((tool) => {
								const fact = tool.metrics?.quality.fact;
								return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
									className: "border-t border-line",
									children: [
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3",
											children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
												type: "button",
												className: "text-left",
												onClick: () => setSelected(tool.id),
												children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "font-medium",
													children: NAMES[tool.id]
												}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
													className: "mt-1 block text-xs text-muted",
													children: "String ceiling, not a product"
												})]
											})
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 text-muted",
											children: "Reference"
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.precision)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.recall)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(fact?.f1)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(tool.metrics?.quality.case.specificity)
										}),
										/* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
											className: "px-4 py-3 font-mono",
											children: pct(tool.metrics?.estate_recall)
										})
									]
								}, tool.id);
							})] })]
						})
					}),
					chart.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "rounded-lg border border-line bg-surface p-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
								className: "text-sm font-medium",
								children: "In-scope fact F1"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-xs text-muted",
								children: "Only surfaces that tool claims to read. 95% bootstrap interval is in the detail."
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-4 h-64",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
									width: "100%",
									height: "100%",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
										data: chart,
										layout: "vertical",
										margin: {
											left: 24,
											right: 8
										},
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
												type: "number",
												domain: [0, 100],
												hide: true
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
												type: "category",
												dataKey: "name",
												width: 140,
												tick: {
													fill: "var(--color-ink)",
													fontSize: 12
												}
											}),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, { formatter: (value) => [`${value}%`, "F1"] }),
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
												dataKey: "f1",
												fill: "var(--color-accent)",
												radius: 2
											})
										]
									})
								})
							})
						]
					}),
					active && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ToolDetail, { tool: active }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Heat, { tools: products })
				]
			}),
			tab === "cases" && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "mt-8",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col gap-3 sm:flex-row",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
								className: "rounded-lg border border-line bg-surface px-3 py-2 text-sm",
								value: surface,
								onChange: (event) => setSurface(event.target.value),
								"aria-label": "Surface",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: "all",
									children: "All surfaces"
								}), SURFACES.map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
									value: item,
									children: item
								}, item))]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("select", {
								className: "rounded-lg border border-line bg-surface px-3 py-2 text-sm",
								value: polarity,
								onChange: (event) => setPolarity(event.target.value),
								"aria-label": "Polarity",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
										value: "all",
										children: "All polarities"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
										value: "positive",
										children: "Positive"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
										value: "negative",
										children: "Negative"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
										value: "near_miss",
										children: "Near miss"
									})
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								className: "flex-1 rounded-lg border border-line bg-surface px-3 py-2 text-sm",
								placeholder: "Filter by id or signal",
								value: query,
								onChange: (event) => setQuery(event.target.value),
								"aria-label": "Filter cases"
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-3 text-xs text-muted",
						children: [visibleCases.length, " cases"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-4 flex flex-col gap-3",
						children: visibleCases.slice(0, 40).map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "rounded-lg border border-line bg-surface p-4",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex flex-wrap items-baseline justify-between gap-2",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
										className: "font-medium",
										children: item.title
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
										className: "font-mono text-xs text-muted",
										children: [
											item.id,
											" · ",
											item.polarity
										]
									})]
								}),
								item.facts.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
									className: "mt-2 flex flex-col gap-1",
									children: item.facts.map((fact) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
										className: "text-sm text-muted",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
												className: "font-mono text-ink",
												children: [
													fact.category,
													":",
													fact.value
												]
											}),
											fact.quote ? ` — “${fact.quote}”` : "",
											fact.path ? ` in ${fact.path}` : ""
										]
									}, `${fact.category}:${fact.value}:${fact.path}`))
								}),
								item.forbidden.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
									className: "mt-2 text-sm text-accent",
									children: ["Must not emit ", item.forbidden.map((fact) => `${fact.category}:${fact.value}`).join(", ")]
								})
							]
						}, item.id))
					})
				]
			}),
			tab === "method" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Method, {})
		]
	});
}
function ToolDetail({ tool }) {
	const quality = tool.metrics?.quality;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
		className: "rounded-lg border border-line bg-surface p-4 sm:p-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xl font-semibold",
				children: NAMES[tool.id] ?? tool.id
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-2 text-sm leading-relaxed text-muted",
				children: tool.status_detail
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "mt-2 font-mono text-xs text-muted",
				children: [
					tool.version || "version not recorded",
					" · surfaces ",
					tool.applicable_surfaces.join(", ") || "none"
				]
			}),
			quality && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
				className: "mt-5 grid grid-cols-2 gap-4 sm:grid-cols-4",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Fact TP / FP / FN",
						value: `${quality.fact.tp} / ${quality.fact.fp} / ${quality.fact.fn}`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Case TP / FP / TN / FN",
						value: `${quality.case.tp} / ${quality.case.fp} / ${quality.case.tn} / ${quality.case.fn}`
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "MCC",
						value: num(quality.case.mcc)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Balanced accuracy",
						value: pct(quality.case.balanced_accuracy)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "F1 95% interval",
						value: quality.fact_f1_ci95 ? `${pct(quality.fact_f1_ci95[0])} – ${pct(quality.fact_f1_ci95[1])}` : "—"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Errors excluded",
						value: String(quality.errors)
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Latency p50",
						value: tool.latency_ms?.p50 != null ? `${tool.latency_ms.p50} ms` : "—"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Stat, {
						label: "Latency p95",
						value: tool.latency_ms?.p95 != null ? `${tool.latency_ms.p95} ms` : "—"
					})
				]
			})
		]
	});
}
function Stat({ label, value }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
		className: "text-xs text-muted",
		children: label
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
		className: "mt-1 font-mono text-sm",
		children: value
	})] });
}
function Heat({ tools }) {
	const scored = tools.filter((tool) => tool.metrics);
	if (scored.length === 0) return null;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "overflow-x-auto rounded-lg border border-line bg-surface p-4",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-sm font-medium",
				children: "Recall by surface"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-xs text-muted",
				children: "Blank means the tool was not asked to read that surface."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
				className: "mt-4 w-full min-w-[40rem] text-left text-xs",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
					className: "text-muted",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
						className: "py-2 pr-3 font-medium",
						children: "Tool"
					}), SURFACES.map((surface) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
						className: "px-1 py-2 font-medium",
						children: surface
					}, surface))]
				}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: scored.map((tool) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("tr", {
					className: "border-t border-line",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
						className: "py-2 pr-3 text-left font-medium",
						children: NAMES[tool.id] ?? tool.id
					}), SURFACES.map((surface) => {
						const cell = tool.metrics?.quality.by_surface[surface];
						const recall = cell?.recall;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "px-1 py-2 font-mono",
							children: cell ? pct(recall) : "·"
						}, surface);
					})]
				}, tool.id)) })]
			})
		]
	});
}
function Method() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
		className: "mt-8 max-w-3xl text-sm leading-relaxed text-muted",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-xl font-semibold text-ink",
				children: "What this measures"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3",
				children: "Each surface holds 25 positives, 15 negatives and 10 near-misses. A positive fact is true only when its quote is in the cited file. A negative case must produce no mapped finding. A near-miss names the lookalike that must not be emitted: Minecraft Bedrock is not AWS Bedrock, a CSS cursor is not the Cursor IDE, Claude Bernard is not Claude."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3",
				children: "These are not private tenant dumps. Identity is an Okta app export, gateways are LiteLLM-style JSONL, low-code is an n8n workflow, SaaS is a Slack approved app, cloud is a Bedrock inventory record, endpoints are home-directory configs, network is a DNS row, runtime is an osquery process list. One documented format per surface. That is the sampling frame."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "mt-8 text-xl font-semibold text-ink",
				children: "How a point is scored"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3",
				children: "Fact-level precision, recall and F1 are primary. A positive case is detected if any planted fact comes back. Any mapped finding on a negative or near-miss is a false positive. Specificity, false-positive rate, balanced accuracy and Matthews correlation use that case table. Crashes and timeouts leave the denominator and are counted as errors. A 1,000-draw bootstrap over cases gives a 95% interval on fact F1."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3",
				children: "Estate recall is the harsher number: positives on surfaces the tool cannot read count as misses. Unscanned negatives are not called true negatives. The lexicon reference applies the published alias list to the artifact text, including paths. It is a string-match ceiling, not an eleventh product."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "mt-8 text-xl font-semibold text-ink",
				children: "What was not done"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3",
				children: "Tools that need a vendor token or a live Kubernetes cluster were probed and then marked not run. Their F1 is left blank on purpose. A zero would pretend the scan happened. Labels were not edited to delete a miss after the tools ran. Alias mapping is a published table, and it does not read the answer key to pick a category."
			})
		]
	});
}
//#endregion
export { Home as component };
