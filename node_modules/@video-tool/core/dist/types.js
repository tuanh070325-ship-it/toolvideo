"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JobStatus = exports.JobType = exports.Platform = void 0;
var Platform;
(function (Platform) {
    Platform["YOUTUBE"] = "youtube";
    Platform["TIKTOK"] = "tiktok";
    Platform["FACEBOOK"] = "facebook";
    Platform["INSTAGRAM"] = "instagram";
    Platform["TWITTER"] = "twitter";
    Platform["GENERIC"] = "generic";
})(Platform || (exports.Platform = Platform = {}));
var JobType;
(function (JobType) {
    JobType["DOWNLOAD"] = "download";
    JobType["EDIT"] = "edit";
    JobType["UPLOAD"] = "upload";
    JobType["TRANSCODE"] = "transcode";
})(JobType || (exports.JobType = JobType = {}));
var JobStatus;
(function (JobStatus) {
    JobStatus["PENDING"] = "pending";
    JobStatus["RUNNING"] = "running";
    JobStatus["COMPLETED"] = "completed";
    JobStatus["FAILED"] = "failed";
    JobStatus["CANCELLED"] = "cancelled";
})(JobStatus || (exports.JobStatus = JobStatus = {}));
//# sourceMappingURL=types.js.map