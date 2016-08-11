# Copyright 2016 MongoDB Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from elftools.dwarf.die import DIE

class DIEInformation(dict):
    def __init__(self, die):
        print die

        # If a type is unnamed, then it's likely a pointer, const, ref, etc. We really only care
        # about the type that it actually identifies, which will later be identified. As such, we
        # can reasonably skip unnamed types, as we don't care about pointers, references, etc.
        if not die.attributes.get('DW_AT_name'):
            return

        name = die.attributes.get('DW_AT_name').value
        tag = die.tag

        size = None
        if die.attributes.get('DW_AT_byte_size'):
            size = die.attributes.get('DW_AT_byte_size').value

        subtype = None
        if die.attributes.get('DW_AT_type'):
            subtype = getSubtype(die)

        members = []
        if die.has_children:
            for child in die.iter_children():
                if child.tag == 'DW_TAG_member':
                    print child
                    memberRef = child.attributes.get('DW_AT_type').value
                    memberType = DIE(die.cu, die.stream, die.cu.cu_offset + memberRef)
                    child = {'name': None, 'type': None}
                    if memberType.attributes.get('DW_AT_name'):
                        members.append(memberType.attributes.get('DW_AT_name').value)
                    else:
                        subtype = getSubtype(memberType)
                        if subtype:
                            members.append(subtype)
                        else:
                            members.append("Cannot determine the type of this member")
                elif child.tag == 'DW_TAG_subprogram':
                    print child
                else:
                    print child

        dict.__init__(self, 
            tag=tag,
            size=size,
            name=name,
            subtype=subtype,
            members=members)

# Some types are actually defined as a more detailed variant on another type. For example, an int*
# is a pointer type with an int subtype so-to-speak. This example represented in DWARF as 
# DW_TAG_pointer_type with a DW_AT_type attribute that points to DW_TAG_base_type with a
# DW_AT_name attribute of "int". 
# If a type defines the DW_AT_type attribute, I call that the subtype.
def getSubtype(die):
    subtype = die
    while subtype.attributes.get('DW_AT_type'):
        print subtype.offset - subtype.cu.cu_offset
        subtypeRef = subtype.attributes.get('DW_AT_type').value
        subtype = DIE(subtype.cu, subtype.stream, subtype.cu.cu_offset + subtypeRef)
        if subtype.attributes.get('DW_AT_name'):
            return subtype.attributes.get('DW_AT_name').value