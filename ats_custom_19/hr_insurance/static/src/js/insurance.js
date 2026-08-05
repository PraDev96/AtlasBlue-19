odoo.define('hr_insurance.update_kanban', function (require) {
'use strict';

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
        console.log("____ elem : ", this.modelName, this.$(".o_insurance_kanban_boxes a").length);
        if (this.modelName === 'insurance.transcation.type' && this.$(".o_insurance_kanban_boxes a").length) {
            this.$('.o_insurance_kanban_boxes a').first().click();
        } else {
            this._super.apply(this, arguments);
        }
    },

});
});


/* @odoo-module */

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { useState } from "@odoo/owl";
import { ProjectTaskKanbanCompiler } from "./project_task_kanban_compiler";
import { SubtaskKanbanList } from "@project/components/subtask_kanban_list/subtask_kanban_list"

export class ProjectTaskKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
        this.state = useState({folded: true});
    }

    /**
     * @override
     */
    get renderingContext() {
        const context = super.renderingContext;
        context["state"] = this.state;
        return context;
    }
}

ProjectTaskKanbanRecord.Compiler = ProjectTaskKanbanCompiler;
ProjectTaskKanbanRecord.components = {
    ...KanbanRecord.components,
    SubtaskKanbanList,
};
